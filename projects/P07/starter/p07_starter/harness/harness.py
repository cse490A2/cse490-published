""" run:
    source .venv-harness/bin/activate
    python harness.py

Additional files:

    .env             the gateway address, key and model metadata.
    settings.json    model select, mcp and tool enabling, general settings.
    skills/          one folder per skill, each holding a SKILL.md.
    systemprompt.md  prompt that gets loaded on every session start.

Every tool call and its reply is appended to trace.jsonl.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Callable
from contextlib import AsyncExitStack, suppress
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).resolve().parent
SETTINGS_PATH = HERE / "settings.json"
PROMPT_PATH = HERE / "systemprompt.md"
CLIENT_NAME = "cse490-harness"
PREVIEW_CHARS = 80  # how much of a tool's result is shown on screen

# Built-in values, used if settings.json doesn't exist
DEFAULT_MODEL_TIMEOUT_SECONDS = 120
DEFAULT_EXECUTE_TIMEOUT_SECONDS = 10
DEFAULT_MAX_TOOL_ROUNDS = 25
DEFAULT_MAX_TOOL_OUTPUT_CHARS = 20000
DEFAULT_MODEL = "external/haiku-5-5"
DEFAULT_SKILLS_FOLDER = "skills"

DEFAULT_SYSTEM_PROMPT = (
    "You are an assistant running inside a harness on the user's machine. You have a range of avaiable tools to use. You are helpful, and provide effective, crystal-clear explanations."
)


# ----------------------------------------------------------------- settings


def load_settings() -> dict:
    """Return settings.json as a dict, or an empty dict when it is absent."""
    if not SETTINGS_PATH.is_file():
        return {}
    try:
        settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        sys.exit(f"settings.json is not valid JSON: {error}")
    except OSError as error:
        sys.exit(f"settings.json could not be read: {error}")
    if not isinstance(settings, dict):
        sys.exit("settings.json must be one object: { ... }")
    return settings


SETTINGS = load_settings()


def setting(section: str, key: str, default: Any) -> Any:
    """Return settings.json's value for section.key, or the built-in default."""
    values = SETTINGS.get(section, {})
    return values.get(key, default) if isinstance(values, dict) else default


# ------------------------------------------------------------------- skills


def load_skills() -> dict[str, dict[str, str]]:
    """Read each skills/<name>/SKILL.md. Return name -> description and text.

    A skill is a folder holding SKILL.md. The file opens with a header
    between --- lines that gives its name and a description of when to use it.
    """
    folder = HERE / setting("skills", "folder", DEFAULT_SKILLS_FOLDER)
    skills: dict[str, dict[str, str]] = {}
    if not folder.is_dir():
        return skills

    for path in sorted(folder.glob("*/SKILL.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            print(f"[skills] skipped {path.parent.name}: {error}")
            continue
        header = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
        fields = dict(
            line.split(":", 1)
            for line in (header.group(1) if header else "").splitlines()
            if ":" in line
        )
        name = fields.get("name", path.parent.name).strip()
        if not fields.get("description", "").strip():
            print(f"[skills] {name} has no description: the model cannot use it")
        skills[name] = {
            "description": fields.get("description", "").strip(),
            "text": text,
        }
    return skills


SKILLS = load_skills()


def skills_index() -> str:
    """Return the list of skills for the system prompt, or an empty string."""
    if not SKILLS:
        return ""
    lines = [f"- {name}: {skill['description']}" for name, skill in SKILLS.items()]
    return (
        "\n\nSkills available (name: when to use). Before doing work a skill "
        "covers, call use_skill with its name and follow what it returns.\n"
        + "\n".join(lines)
    )


def use_skill(name: str) -> str:
    """Load a skill's full instructions.

    Call it before doing work a listed skill covers, then follow what it
    returns.

    Args:
        name: Name of the skill, as the skills list shows it.
    """
    if name in SKILLS:
        return SKILLS[name]["text"]
    return f"Error: no skill named {name!r}. Skills: {', '.join(SKILLS) or 'none'}"


# -------------------------------------------------------------------- trace
#
# trace.py writes one line to trace.jsonl for each thing the agent does, and
# the agent view reads that file. With trace.py beside this file the trace is
# on. Without it the harness works the same and writes no trace.

try:
    from trace import SESSION_ID, append_trace, trace_model_call

    TRACING = True
except ImportError:  # no trace.py beside this file (Python's own "trace" is not it)
    TRACING = False
    SESSION_ID = str(uuid.uuid4())

    def append_trace(kind: str, **fields: Any) -> None:
        """Do nothing: tracing is off."""

    def trace_model_call(*args: Any, **fields: Any) -> None:
        """Do nothing: tracing is off."""


# -------------------------------------------------------------------- model


class GatewayError(Exception):
    """A failed model call: what happened, and what to try."""

    def __init__(self, what: str, hint: str, code: int | None = None) -> None:
        """Keep the two lines the user is shown, and the HTTP status if any."""
        super().__init__(what)
        self.hint = hint
        self.code = code


# These are internally-tracked errors:
LOCAL_NOTES = {
    401: "The key is LITELLM_API_KEY in .env.",
    502: "A request that takes over a minute is cut off here. Ask for less "
    "in one step, or wait if many requests are running.",
}


def gateway_message(body: str) -> str:
    """Return the gateway's own error message from the body of its reply.

    The gateway answers an error with {"error": {"message": ...}}, or with
    {"detail": ...} for a path it does not have. Anything else (the proxy's
    HTML page on a 502) is returned as plain text, cut short.
    """
    try:
        reply = json.loads(body)
        message = reply["error"]["message"] if "error" in reply else reply["detail"]
    except (ValueError, KeyError, TypeError):
        message = re.sub(r"<[^>]+>", " ", body)
    return " ".join(str(message).split())[:300]


def send(request: urllib.request.Request) -> tuple[dict, dict]:
    """Send one request. Return the gateway's reply and its headers.

    Raise GatewayError, with a hint, when the request fails.
    """
    timeout = setting("model", "timeout_seconds", DEFAULT_MODEL_TIMEOUT_SECONDS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as reply:
            body = json.loads(reply.read())
            body["choices"][0]["message"]  # a reply without one is unreadable
            return body, dict(reply.headers.items())
    except urllib.error.HTTPError as error:
        message = gateway_message(error.read().decode(errors="replace"))
        what = f"the gateway answered {error.code}: {message}"
        hint = LOCAL_NOTES.get(error.code, "")
        raise GatewayError(what, hint, error.code) from error
    except TimeoutError as error:
        hint = "raise timeout_seconds under model in settings.json, or ask for less."
        raise GatewayError(f"no reply in {timeout} seconds", hint) from error
    except urllib.error.URLError as error:
        hint = "off campus, connect the UW VPN (Husky OnNet)."
        what = f"the gateway did not answer: {error.reason}"
        raise GatewayError(what, hint) from error
    except (ValueError, KeyError, IndexError, TypeError) as error:
        hint = "the gateway replied, but not with a model message: try again."
        raise GatewayError(f"unreadable reply: {error!r}", hint) from error


def chat_request(context: list[dict], tools: list[dict]) -> urllib.request.Request:
    """Build the request that sends the conversation to the gateway."""
    base = os.environ["LITELLM_BASE_URL"].rstrip("/")
    path = "/chat/completions" if base.endswith("/v1") else "/v1/chat/completions"
    return urllib.request.Request(
        base + path,
        data=json.dumps(
            {
                "model": setting("model", "default", DEFAULT_MODEL),
                "messages": context,
                "tools": tools,
            }
        ).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.environ['LITELLM_API_KEY']}",
            "User-Agent": f"{CLIENT_NAME} ({SESSION_ID})",
        },
    )


def call_model(context: list[dict], tools: list[dict]) -> dict:
    """Send the conversation to the gateway and return the model's message.

    Every call, answered or failed, is recorded in trace.jsonl.
    """
    started = time.time()
    try:
        body, headers = send(chat_request(context, tools))
    except GatewayError as error:
        trace_model_call(context, started, error=error)
        raise
    trace_model_call(context, started, body, headers)
    return body["choices"][0]["message"]


# -------------------------------------------------------------- local tools


def checked(path: str) -> Path:
    """Return the resolved path. Refuse one outside this folder, or a key file."""
    target = (Path.cwd() / path).resolve()
    outside = Path.cwd().resolve() not in (target, *target.parents)
    if outside or target.name == ".env" or target.name.startswith(".env."):
        raise ValueError(f"{path!r} is outside this folder or is a key file")
    return target


def read_file(path: str) -> str:
    """Read the contents of a file from disk.

    Args:
        path: Path of the file to read.
    """
    return checked(path).read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    """Write text to a file, creating or overwriting it.

    Args:
        path: Path of the file to write.
        content: Full text to write.
    """
    target = checked(path)
    target.parent.mkdir(parents=True, exist_ok=True)  # a new folder is made as needed
    target.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} chars to {path}"


def execute(path: str) -> str:
    """Run a Python file and return its output.

    Args:
        path: Path of the .py file to run.
    """
    result = subprocess.run(
        [sys.executable, str(checked(path))],
        capture_output=True,
        text=True,
        timeout=setting(
            "tools", "execute_timeout_seconds", DEFAULT_EXECUTE_TIMEOUT_SECONDS
        ),
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    return f"exit {result.returncode}: {output or '(no output)'}"


def definition(function: Callable[..., str]) -> dict:
    """Build a tool's definition from the function itself.

    The name is the function's name. The description is its docstring, up to
    "Args:". Each argument's description is its line under "Args:".
    """
    summary, _, args = (inspect.getdoc(function) or "").partition("Args:")
    described = dict(re.findall(r"(?m)^\s*(\w+):\s*(.+)$", args))
    arguments = list(inspect.signature(function).parameters)
    return {
        "type": "function",
        "function": {
            "name": function.__name__,
            "description": " ".join(summary.split()),
            "parameters": {
                "type": "object",
                "properties": {
                    name: {"type": "string", "description": described.get(name, name)}
                    for name in arguments
                },
                "required": arguments,
            },
        },
    }


# To add a local tool: write its function above, then add its name here.
# The model reads the function's docstring to learn what the tool does.
LOCAL_TOOLS = [read_file, write_file, execute, use_skill]

LOCAL_FUNCTIONS = {function.__name__: function for function in LOCAL_TOOLS}
LOCAL_DEFINITIONS = [definition(function) for function in LOCAL_TOOLS]


def run_local_tool(name: str, args: dict) -> str | None:
    """Run a local tool. Return None when the name is not in LOCAL_TOOLS."""
    if name not in LOCAL_FUNCTIONS:
        return None
    try:
        return str(LOCAL_FUNCTIONS[name](**args))
    except subprocess.TimeoutExpired as error:
        return f"Error: still running after {error.timeout} seconds, so it was stopped"
    except Exception as error:  # a tool's failure is the model's to read
        return f"Error: {type(error).__name__}: {error}"


# ------------------------------------------------------------- server tools


def expand_env(value: str) -> str:
    """Replace each ${NAME} in a settings value with the environment's NAME."""
    return re.sub(
        r"\$\{(\w+)\}", lambda match: os.environ.get(match.group(1), ""), value
    )


def server_parameters(entry: dict) -> StdioServerParameters:
    """Turn one mcpServers entry into the parameters that start the server."""
    extra = {key: expand_env(str(val)) for key, val in entry.get("env", {}).items()}
    return StdioServerParameters(
        command=entry["command"],
        args=list(entry.get("args", [])),
        env={**os.environ, **extra},
    )


READ_ONLY_SERVER_TOOLS: set[str] = set()  # filled as each server lists its tools


def read_only(tool: Any) -> bool:
    """Return whether a server marks a tool as one that changes nothing."""
    notes = getattr(tool, "annotations", None)
    return bool(
        getattr(notes, "read_only_hint", None) or getattr(notes, "readOnlyHint", None)
    )


def tool_schema(tool: Any) -> dict:
    """Return a server tool's input schema under either name the SDK uses."""
    return getattr(tool, "input_schema", None) or getattr(tool, "inputSchema", {})


async def start_servers(
    stack: AsyncExitStack, entries: dict
) -> tuple[list[dict], dict[str, ClientSession]]:
    """Start every server in mcpServers. Return their tools and who owns each.

    Every tool a server reports is offered to the model. To offer fewer,
    narrow the server itself in settings.json (GitHub's takes --tools).
    """
    tools: list[dict] = []
    sessions: dict[str, ClientSession] = {}

    for server_name, entry in entries.items():
        if not isinstance(entry, dict) or "command" not in entry:
            print(f'[mcp] {server_name}: its entry in settings.json needs a "command"')
            continue
        try:
            read, write = await stack.enter_async_context(
                stdio_client(server_parameters(entry))
            )
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            listed = (await session.list_tools()).tools
        except Exception as error:  # one bad server must not stop the harness
            print(f"[mcp] {server_name}: did not start: {error}")
            print(f"[mcp] {server_name}: its own message, if it gave one, is above.")
            continue

        for tool in listed:
            sessions[tool.name] = session
            if read_only(tool):
                READ_ONLY_SERVER_TOOLS.add(tool.name)
            tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool_schema(tool),
                    },
                }
            )
        append_trace(
            "server_tools", server=server_name, tools=[tool.name for tool in listed]
        )
        print(f"[mcp] {server_name}: {len(listed)} tools")

    return tools, sessions


def part_as_dict(part: Any) -> dict:
    """Turn one part of a server's reply into a plain dict."""
    kind = getattr(part, "type", None)
    if kind == "text":
        return {"type": "text", "text": getattr(part, "text", "")}
    if kind == "image":
        return {
            "type": "image",
            "data": getattr(part, "data", ""),
            "mimeType": getattr(part, "mimeType", "image/png"),
        }
    if hasattr(part, "model_dump"):
        return part.model_dump()
    return {"type": "text", "text": str(part)}


def part_text(part: dict) -> str:
    """Return the text a part carries: its own, or its embedded file's."""
    if part["type"] == "text":
        return part["text"]
    if part["type"] == "resource":
        return (part.get("resource") or {}).get("text") or ""
    return ""


def content_for_model(parts: list[dict], structured: Any) -> str | list[dict]:
    """Shape a server's reply the way the chat API takes a tool result."""
    images = [part for part in parts if part["type"] == "image"]
    texts = [text for text in map(part_text, parts) if text]

    if images:
        blocks: list[dict] = [{"type": "text", "text": text} for text in texts]
        for image in images:
            url = f"data:{image['mimeType']};base64,{image['data']}"
            blocks.append({"type": "image_url", "image_url": {"url": url}})
        return blocks

    if texts:
        return "\n".join(texts)
    return json.dumps(structured) if structured is not None else ""


async def run_server_tool(
    session: ClientSession, name: str, args: dict
) -> tuple[str | list[dict], Any]:
    """Ask a server to run a tool.

    Return its result twice: shaped for the model, and whole for the trace.
    """
    try:
        reply = await session.call_tool(name, arguments=args)
    except Exception as error:  # a server may raise anything; the model sees it
        return f"Error: {error}", f"Error: {error}"
    parts = [part_as_dict(part) for part in reply.content]
    structured = getattr(reply, "structuredContent", None)
    logged = {"isError": bool(getattr(reply, "isError", False)), "content": parts}
    return content_for_model(parts, structured), logged


# ---------------------------------------------------------------- plan mode
#
#   /plan <goal>    look and ask, change nothing, write the plan to PLAN.md
#   (you reply)     answer its questions, or ask for changes to the plan
#   /approve        the plan is accepted: changes are allowed, the work starts
#   /cancel         leave plan mode with nothing done

PLAN_PATH = Path("PLAN.md")
PLAN: dict[str, Any] = {"active": False, "started": 0.0}

# Local tools that change nothing. A server says which of its own are read-only.
READ_ONLY_TOOLS = {"read_file", "use_skill"}

PLAN_INSTRUCTIONS = (
    "Plan mode is on. Change nothing yet: every tool that writes, runs or "
    "modifies is refused until the user approves the plan.\n"
    "1. Read what you need with the read-only tools.\n"
    "2. If the goal leaves open something that would change the plan, ask the "
    "user, one question at a time, and wait for each answer.\n"
    "3. Write the plan to PLAN.md with write_file, the one write allowed: the "
    "goal in one line, the steps in order, the files each step changes, how "
    "each step will be checked, and the risks or open questions.\n"
    "4. Reply with a short summary of the plan and say you are waiting for "
    "/approve. If the user asks for changes, update PLAN.md and wait again."
)


def plan_refusal(name: str, args: dict) -> str | None:
    """Return why plan mode refuses a tool call, or None when it may run."""
    if not PLAN["active"] or name in READ_ONLY_TOOLS | READ_ONLY_SERVER_TOOLS:
        return None
    with suppress(ValueError, TypeError):
        if name == "write_file" and checked(args["path"]) == checked(str(PLAN_PATH)):
            return None
    return (
        f"refused: plan mode is on, and {name} can change things. Write the "
        "plan to PLAN.md and wait for the user to type /approve."
    )


def plan(goal: str, context: list[dict]) -> str | None:
    """/plan <goal>: plan the work first; nothing changes until /approve."""
    if not goal:
        print("[plan] say the goal: /plan <goal>")
        return None
    PLAN.update(active=True, started=time.time())
    append_trace("plan_start", goal=goal)
    print("[plan] plan mode is on: nothing changes until you type /approve.")
    instructions = SKILLS.get("plan-mode", {}).get("text") or PLAN_INSTRUCTIONS
    return f"{instructions}\n\nGoal: {goal}"


def approve(note: str, context: list[dict]) -> str | None:
    """/approve: accept the plan in PLAN.md and start the work."""
    if not PLAN["active"]:
        print("[plan] there is no plan to approve: start with /plan <goal>")
        return None
    written = PLAN_PATH.is_file() and PLAN_PATH.stat().st_mtime >= PLAN["started"]
    if not written:
        print("[plan] no plan has been written to PLAN.md yet: ask for it first.")
        return None
    PLAN["active"] = False
    append_trace("plan_approved", plan=PLAN_PATH.read_text(encoding="utf-8"))
    print("[plan] approved: plan mode is off, and the work starts.")
    return (
        "The plan in PLAN.md is approved. Carry it out now, one step at a "
        "time, and check each step the way the plan says. If a step cannot be "
        f"done as planned, stop and say why. {note}".strip()
    )


def cancel(note: str, context: list[dict]) -> str | None:
    """/cancel: leave plan mode with nothing done."""
    if not PLAN["active"]:
        print("[plan] plan mode is not on.")
        return None
    PLAN["active"] = False
    append_trace("plan_cancelled")
    print("[plan] cancelled: plan mode is off. Only PLAN.md may have been written.")
    context.append(
        {"role": "user", "content": "I cancelled the plan. Do not carry it out."}
    )
    return None


# --------------------------------------------------------------------- loop


# To add a command: write its function above, then add its name here.
# A command is typed in the chat as /name; the model cannot run one.
COMMANDS = [plan, approve, cancel]

COMMAND_FUNCTIONS = {function.__name__: function for function in COMMANDS}


async def run_command(line: str, context: list[dict]) -> str | None:
    """Run a /command. Return a prompt for the model, or None with none to send."""
    name, _, rest = line[1:].partition(" ")
    if name not in COMMAND_FUNCTIONS:
        known = ", ".join(f"/{command}" for command in COMMAND_FUNCTIONS)
        print(f"[harness] no command /{name}. Commands: {known}")
        return None
    result = COMMAND_FUNCTIONS[name](rest.strip(), context)
    return await result if inspect.isawaitable(result) else result


async def in_background(function: Callable[..., Any], *args: Any) -> Any:
    """Run a blocking function in a thread and wait for it without blocking.

    The thread is a daemon: when the harness is told to stop (Ctrl+C), it
    leaves at once and does not wait for a prompt or a model reply to finish.
    """
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()

    def finish(result: Any, error: BaseException | None) -> None:
        if future.done():  # the harness stopped waiting
            return
        if error is None:
            future.set_result(result)
        else:
            future.set_exception(error)

    def work() -> None:
        try:
            result, error = function(*args), None
        except BaseException as raised:  # handed to whoever is waiting
            result, error = None, raised
        with suppress(RuntimeError):  # the loop has already closed
            loop.call_soon_threadsafe(finish, result, error)

    threading.Thread(target=work, daemon=True).start()
    return await future


def answer_without_server(
    name: str, args: dict | None, sessions: dict[str, ClientSession], deny: set[str]
) -> str | None:
    """Return a tool call's result when no server is needed, else None."""
    if args is None:
        return "Error: the arguments are not JSON"
    if name in deny:
        return (
            f"refused: {name} matches a deny entry under permissions in settings.json"
        )
    if plan_refusal(name, args):
        return plan_refusal(name, args)
    if name in LOCAL_FUNCTIONS:
        return run_local_tool(name, args)
    if name not in sessions:
        return f"Error: no tool named {name}"
    return None


async def run_tool(
    tool_call: dict, sessions: dict[str, ClientSession], deny: set[str]
) -> str | list[dict]:
    """Run one tool call, local or on a server, and record it in the trace."""
    name = tool_call["function"]["name"]
    try:
        args = json.loads(tool_call["function"]["arguments"] or "{}")
    except json.JSONDecodeError:
        args = None
    append_trace("tool_call", name=name, arguments=args)

    result = logged = answer_without_server(name, args, sessions, deny)
    if result is None:
        result, logged = await run_server_tool(sessions[name], name, args)
    append_trace("tool_reply", name=name, reply=logged)
    return result


async def answer(
    context: list[dict],
    tools: list[dict],
    sessions: dict[str, ClientSession],
    deny: set[str],
) -> None:
    """Call the model until it replies in plain text, running tools between.

    When the model cannot be reached, the whole unanswered turn is removed
    from the conversation, so the next prompt starts from a clean state.
    """
    turn_start = len(context) - 1  # the prompt this turn is answering
    max_rounds = setting("model", "max_tool_rounds", DEFAULT_MAX_TOOL_ROUNDS)
    max_chars = setting("tools", "max_output_chars", DEFAULT_MAX_TOOL_OUTPUT_CHARS)

    for _ in range(max_rounds):
        try:
            reply = await in_background(call_model, context, tools)
        except GatewayError as error:
            print(f"[harness] {error}")
            if error.hint:
                print(f"[harness] {error.hint}")
            del context[turn_start:]
            return

        context.append(reply)
        if not reply.get("tool_calls"):
            print(reply.get("content") or "")
            return

        for tool_call in reply["tool_calls"]:
            result = await run_tool(tool_call, sessions, deny)
            if isinstance(result, str) and len(result) > max_chars:
                result = (
                    f"{result[:max_chars]}\n[cut: the tool returned {len(result)} "
                    f"characters; the first {max_chars} are shown]"
                )
            preview = result if isinstance(result, str) else json.dumps(result)
            print(
                f"[harness] {tool_call['function']['name']} -> "
                f"{preview[:PREVIEW_CHARS]}"
            )
            context.append(
                {"role": "tool", "tool_call_id": tool_call["id"], "content": result}
            )

    print(
        f"[harness] stopped after {max_rounds} rounds of tool calls "
        "(max_tool_rounds under model in settings.json)."
    )


async def main() -> None:
    """Start the servers, then read prompts until the input ends."""
    deny = set(setting("permissions", "deny", []))
    prompt = (
        PROMPT_PATH.read_text(encoding="utf-8")
        if PROMPT_PATH.is_file()
        else DEFAULT_SYSTEM_PROMPT
    )

    async with AsyncExitStack() as stack:
        server_tools, sessions = await start_servers(
            stack, SETTINGS.get("mcpServers", {})
        )
        tools = LOCAL_DEFINITIONS + server_tools
        context = [{"role": "system", "content": prompt + skills_index()}]
        if SKILLS:
            print(f"[skills] {len(SKILLS)} loaded: {', '.join(SKILLS)}")
        if not TRACING:
            print("[trace] off: put trace.py beside harness.py to turn it on.")

        while True:
            try:
                ask = "plan >>> " if PLAN["active"] else ">>> "
                user = (await in_background(input, ask)).strip()
            except EOFError:  # Ctrl+D, or the end of piped input
                return
            if user in {"exit", "quit"}:
                return
            if not user:
                continue
            if user.startswith("/"):
                user = await run_command(user, context)
                if user is None:  # the command did all there was to do
                    continue
            context.append({"role": "user", "content": user})
            await answer(context, tools, sessions, deny)


if __name__ == "__main__":
    load_dotenv(HERE / ".env")
    missing = [
        name
        for name in ("LITELLM_BASE_URL", "LITELLM_API_KEY")
        if not os.environ.get(name)
    ]
    if missing:
        sys.exit(f".env is missing {' and '.join(missing)}")
    with suppress(KeyboardInterrupt):  # Ctrl+C is a normal way to leave
        asyncio.run(main())
    print("\n[harness] stopped.")
