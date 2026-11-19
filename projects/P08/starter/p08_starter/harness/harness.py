"""
run:
    source .venv-harness/bin/activate
    python harness.py

Additional files:

    .env             the gateway address, key and model metadata.
    settings.json    model select, mcp and tool enabling, general settings.
    skills/          one folder per skill, each holding a SKILL.md.
    systemprompt.md  prompt that gets loaded on every session start.
    trace.jsonl      harness log file.
"""

from __future__ import annotations

import argparse
import asyncio
import inspect
import itertools
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
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
TRACE_PATH = Path("trace.jsonl")

CLIENT_NAME = "cse490-harness"
# One id per start of the chat. A manager and its helpers are handed the
# chat's id, so every line of one sitting can be found together.
SESSION_ID = os.environ.get("HARNESS_SESSION") or str(uuid.uuid4())
RUN_ID = os.environ.get("HARNESS_RUN")  # set for the agents of one /spawn run
PREVIEW_CHARS = 80  # how much of a tool's result is shown on screen

# Built-in values, used if settings.json doesn't exist
DEFAULT_MODEL_TIMEOUT_SECONDS = 120
DEFAULT_EXECUTE_TIMEOUT_SECONDS = 10
DEFAULT_MAX_TOOL_ROUNDS = 25
DEFAULT_MAX_TOOL_OUTPUT_CHARS = 20000
DEFAULT_MODEL = "external/haiku-5-5"
DEFAULT_SKILLS_FOLDER = "skills"
DEFAULT_HELPER_MODEL = "external/haiku-5-5"
DEFAULT_MAX_HELPERS = 8
DEFAULT_SPAWN_MINUTES = 5
DEFAULT_ROUTER_DECIDER_URL = "http://127.0.0.1:8000/v1/systemone"
DEFAULT_ROUTER_FALLBACK_MODEL = "external/haiku-5-5"
DEFAULT_ROUTER_THRESHOLD = 0.5
DEFAULT_ROUTER_QUESTIONS = {
    "quality": {
        "question": "Does the response correctly and completely answer the user's question?"
    }
}
DEFAULT_ROUTER_TIMEOUT_SECONDS = 60
DEFAULT_ROUTER_MAX_STATE_CHARS = 12000
ROUTER_DETECTION_CUT = 0.5  # detection at or above this: the reply holds program code
ROUTER_RESULT_CHARS = 600  # how much of one tool result the decider is shown

# Who this process is. A plain start is the chat, "main". /spawn starts a
# manager, and the manager starts helpers: each is a copy of this program.
AGENT: dict[str, Any] = {
    "name": "main",
    "role": None,  # None, "manager" or "helper"
    "task": None,  # the one prompt a manager or a helper runs
    "model": None,  # None means the default model in settings.json
    "deadline": None,  # the clock time a /spawn run must end by
}
REPORT_MARK = "=== report ==="  # a manager or helper prints its report after this

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


def append_trace(kind: str, **fields: Any) -> None:
    """Append one event to trace.jsonl, stamped with when and by whom."""
    line = {
        "type": kind,
        "time": utc(time.time()),
        "session": SESSION_ID,
        "run": RUN_ID,
        "agent": AGENT["name"],
        **fields,
    }
    with TRACE_PATH.open("a", encoding="utf-8") as trace:
        trace.write(json.dumps(line) + "\n")


def utc(seconds: float) -> str:
    """Return a clock time as the gateway's logs write it: UTC, to the millisecond."""
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(seconds))
    return f"{stamp}.{int(seconds % 1 * 1000):03d}Z"


def number(text: str | None) -> float | None:
    """Return a header's value as a number, or None when it is absent."""
    try:
        return float(text) if text is not None else None
    except ValueError:
        return None


def model_call_record(
    context: list[dict], started: float, ended: float, body: dict, headers: dict
) -> dict:
    """Describe one model call in the field names of the gateway's own logs.

    The gateway keeps a record of every call under these names. Writing the
    same names here lets a line of trace.jsonl be matched to the gateway's
    record of the same call by session.litellm_call_id or request_id.
    """
    usage = body.get("usage") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}
    choice = (body.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    tool_calls = message.get("tool_calls") or []
    asked_by_user = bool(context) and context[-1].get("role") == "user"
    return {
        "request_id": body.get("id"),
        "finish_reason": choice.get("finish_reason"),
        "response_text": message.get("content"),
        "tool_names": [call["function"]["name"] for call in tool_calls] or None,
        "turn": {
            "origin": "user" if asked_by_user else "automated",
            "user_prompt": context[-1].get("content") if asked_by_user else None,
        },
        "model": {
            "model_group": headers.get("x-litellm-model-group") or body.get("model"),
            "model": headers.get("x-litellm-model-name"),
            "model_id": headers.get("x-litellm-model-id"),
        },
        "tokens": {
            "prompt": usage.get("prompt_tokens"),
            "completion": usage.get("completion_tokens"),
            "total": usage.get("total_tokens"),
            "reasoning": completion_details.get("reasoning_tokens"),
            "cache_read": prompt_details.get("cached_tokens"),
            "cache_creation": prompt_details.get("cache_creation_tokens"),
        },
        "spend": number(headers.get("x-litellm-response-cost")),
        "key": {
            "spend": number(headers.get("x-litellm-key-spend")),
            "max_budget": number(headers.get("x-litellm-key-max-budget")),
        },
        "timestamps": {
            "start_time": utc(started),
            "end_time": utc(ended),
            "request_duration_ms": round((ended - started) * 1000),
            "gateway_duration_ms": number(
                headers.get("x-litellm-response-duration-ms")
            ),
        },
        "session": {
            "session_id": SESSION_ID,
            "litellm_call_id": headers.get("x-litellm-call-id"),
        },
        "client": {"name": CLIENT_NAME, "messages_sent": len(context)},
    }


def trace_model_call(
    context: list[dict],
    started: float,
    body: dict | None = None,
    headers: dict | None = None,
    error: GatewayError | None = None,
) -> None:
    """Record one model call, answered or failed, in trace.jsonl."""
    append_trace(
        "model_call",
        status="failure" if error else "success",
        error_code=error.code if error else None,
        error_message=str(error) if error else None,
        **model_call_record(context, started, time.time(), body or {}, headers or {}),
    )


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


def chat_request(
    context: list[dict], tools: list[dict], model: str | None = None
) -> urllib.request.Request:
    """Build the request that sends the conversation to the gateway.

    A model given here is sent in place of the agent's model for this request.
    """
    base = os.environ["LITELLM_BASE_URL"].rstrip("/")
    path = "/chat/completions" if base.endswith("/v1") else "/v1/chat/completions"
    return urllib.request.Request(
        base + path,
        data=json.dumps(
            {
                "model": model
                or AGENT["model"]
                or setting("model", "default", DEFAULT_MODEL),
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


def call_model(context: list[dict], tools: list[dict], model: str | None = None) -> dict:
    """Send the conversation to the gateway and return the model's message.

    Every call, answered or failed, is recorded in trace.jsonl.
    """
    started = time.time()
    try:
        body, headers = send(chat_request(context, tools, model))
    except GatewayError as error:
        trace_model_call(context, started, error=error)
        raise
    trace_model_call(context, started, body, headers)
    return body["choices"][0]["message"]


# ------------------------------------------------------------------- router
#
#   default model replies  ->  judge() asks the decider every question under
#   router.questions in settings.json, in one call, and gets one number per name
#        quality alone:      quality below router.threshold -> the fallback model answers
#        quality and detection: detection at least 0.5 and quality below
#                               router.threshold -> the fallback model answers
#        otherwise, or the decider cannot be reached: the reply is kept


def tool_lines(steps: list[dict]) -> str:
    """Write a turn's tool calls as numbered lines, each with its result."""
    results = {
        step.get("tool_call_id"): step.get("content")
        for step in steps
        if step.get("role") == "tool"
    }
    lines = []
    for step in steps:
        for call in step.get("tool_calls") or []:
            result = results.get(call.get("id"), "")
            if not isinstance(result, str):
                result = json.dumps(result)
            result = " ".join(result.split())
            if len(result) > ROUTER_RESULT_CHARS:
                result = result[:ROUTER_RESULT_CHARS] + " [cut]"
            function = call["function"]
            lines.append(
                f"{len(lines) + 1}. {function['name']}({function['arguments']})"
                f" -> {result}"
            )
    return "\n".join(lines) or "(no tools used)"


def judge(question: str, response: str, steps: list[dict]) -> dict | None:
    """Ask the decider about the reply. Return None when it fails.

    One call carries every question under router.questions in settings.json:
    the one named quality and, when the settings hold one, the one named
    detection. Each goes to the decider under its own name as a yes/no question.
    Return the decider's number for each name, such as {"quality": 0.87} or
    {"quality": 0.31, "detection": 0.92}.
    Every judgment, made or failed, is recorded in trace.jsonl.
    """
    asked = setting("router", "questions", DEFAULT_ROUTER_QUESTIONS)
    if not isinstance(asked, dict) or "quality" not in asked:
        print("[router] settings.json has no question named quality; keeping the reply.")
        append_trace(
            "router_judge", status="failure", error_message="no question named quality"
        )
        return None
    # The decider's own form: a yes/no question is {"type": "noul", "instructions": ...}.
    questions = {
        name: {"type": "noul", "instructions": entry["question"]}
        for name, entry in asked.items()
        if isinstance(entry, dict) and isinstance(entry.get("question"), str)
    }
    limit = setting("router", "max_state_chars", DEFAULT_ROUTER_MAX_STATE_CHARS)
    lines = tool_lines(steps)
    tools = lines[: limit // 2]
    # The response keeps its end, where the code usually is, and may use the room
    # the tool lines left of their half.
    room = limit // 3 + (limit // 2 - len(tools))
    timeout = setting("router", "timeout_seconds", DEFAULT_ROUTER_TIMEOUT_SECONDS)

    def ask(room: int) -> dict:
        """Send the decider the state, with at most `room` characters of the response."""
        kept = response if len(response) <= room else "[cut] " + response[-room:]
        state = "\n\n".join(
            [
                "User question:\n" + question[: limit // 6],
                "Tools the model used, with their results:\n" + tools,
                "Model response:\n" + kept,
            ]
        )
        request = urllib.request.Request(
            setting("router", "decider_url", DEFAULT_ROUTER_DECIDER_URL),
            data=json.dumps({"state": state, "questions": questions}).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as reply:
            return json.loads(reply.read())["answers"]

    started = time.time()
    try:
        try:
            answers = ask(room)
        except urllib.error.HTTPError as error:
            if error.code != 422:
                raise
            # The decider reads at most 4096 tokens and refuses more: send half as much.
            answers = ask(room // 2)
        numbers = {name: float(answers[name]["noul"]) for name in questions}
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"[router] decider unreachable ({error}); keeping the reply.")
        append_trace("router_judge", status="failure", error_message=str(error))
        return None
    fields = {
        **numbers,  # one field for each question's name: quality, and detection when asked
        "status": "success",
        "question": question,
        "tools_used": lines,
        "response": response,
        "duration_ms": round((time.time() - started) * 1000),
    }
    append_trace("router_judge", **fields)
    return numbers


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


JSON_TYPES = {
    "str": {"type": "string"},
    "list[str]": {"type": "array", "items": {"type": "string"}},
}


def definition(function: Callable[..., str]) -> dict:
    """Build a tool's definition from the function itself.

    The name is the function's name. The description is its docstring, up to
    "Args:". Each argument's description is its line under "Args:".
    """
    summary, _, args = (inspect.getdoc(function) or "").partition("Args:")
    described = dict(re.findall(r"(?m)^\s*(\w+):\s*(.+)$", args))
    parameters = inspect.signature(function).parameters
    arguments = list(parameters)
    return {
        "type": "function",
        "function": {
            "name": function.__name__,
            "description": " ".join(summary.split()),
            "parameters": {
                "type": "object",
                "properties": {
                    name: {
                        **JSON_TYPES.get(str(parameter.annotation), JSON_TYPES["str"]),
                        "description": described.get(name, name),
                    }
                    for name, parameter in parameters.items()
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


# ---------------------------------------------------------- orchestration
#
#   /spawn <goal>     typed in the chat; the model cannot start it
#        |
#     manager         a copy of this program: splits the goal into tasks
#        |
#     helpers         copies of this program, one task each, all at once
#        |
#     manager         reads their reports: done, or another round
#        |
#     report          printed in the chat and added to the conversation


def start_helpers(tasks: list[str]) -> str:
    """Start one helper per task, all at once, and return their reports.

    A helper is a fresh copy of this program: it knows only its task. Give
    each task what to do, which files it owns, and what done means.

    Args:
        tasks: One task per helper, each complete on its own.
    """
    limit = setting("spawn", "max_helpers", DEFAULT_MAX_HELPERS)
    if not isinstance(tasks, list) or not tasks:
        return "Error: tasks must be a list with at least one task"
    if len(tasks) > limit:
        return (
            f"refused: {len(tasks)} helpers in one call is over max_helpers "
            f"{limit} under spawn in settings.json"
        )

    running = []
    for task in tasks:
        name = f"helper-{next(HELPER_NUMBERS)}"
        # closed below, once the helper has ended and its output is read
        output = tempfile.TemporaryFile(mode="w+", encoding="utf-8")  # noqa: SIM115
        process = subprocess.Popen(
            child_command("helper", name, str(task)),
            stdin=subprocess.DEVNULL,
            stdout=output,
            stderr=subprocess.STDOUT,
        )
        append_trace("helper_start", helper=name, task=str(task))
        print(f"[spawn] started {name}", flush=True)
        running.append((name, process, output))

    reports = []
    for name, process, output in running:
        code: int | str
        try:
            code = process.wait(timeout=seconds_left())
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            code = "stopped at the time limit"
        output.seek(0)
        report = report_from(output.read(), code)
        output.close()
        append_trace("helper_report", helper=name, exit_code=code, report=report)
        print(f"[spawn] {name} reported", flush=True)
        reports.append(f"## {name}\n{report}")
    return "\n\n".join(reports)


HELPER_NUMBERS = itertools.count(1)  # helper-1, helper-2, ... across every call

# What a role changes about a copy of this program: its prompt, its model
# (a key under spawn in settings.json, and the model used without one), the
# tools it gains, and the tools it is refused.
ROLES: dict[str, dict[str, Any]] = {
    "manager": {
        "model": ("manager_model", None),
        "tools": [start_helpers],
        "deny": {"write_file"},
        "prompt": (
            "You are the manager of a team of agents working in this folder. "
            "The user gives you one goal. Split it into tasks that do not touch "
            "the same files, and start one helper per task with start_helpers, "
            "all in one call. A helper starts with no memory of this "
            "conversation, so each task must say what to do, which files the "
            "helper owns, and what done means. Read the reports, then check the "
            "work yourself with your tools. Send a task that failed back to a "
            "new helper with what went wrong. You cannot write files: a helper "
            "does. When the goal is met, or cannot be, reply with a short "
            "report: what was done, what was not, and what you checked."
        ),
    },
    "helper": {
        "model": ("helper_model", DEFAULT_HELPER_MODEL),
        "tools": [],
        "deny": set(),
        "prompt": (
            "You are a helper on a team of agents working in this folder. You "
            "have one task from the manager and no other context. Do that task "
            "and nothing more. Touch only the files it names. When you are "
            "done, reply with a short report: what you did, the files you "
            "changed, and anything the task left unclear."
        ),
    },
}


def role_model(role: str) -> str | None:
    """Return the model a role runs on, or None for the default model."""
    key, fallback = ROLES[role]["model"]
    return setting("spawn", key, fallback)


def child_command(role: str, name: str, task: str) -> list[str]:
    """Return the command that starts a copy of this program in a role."""
    program = str(Path(__file__).resolve())
    return [sys.executable, program, "--role", role, "--name", name, "--task", task]


def seconds_left() -> float | None:
    """Return the seconds until this run must end, or None with no limit."""
    if AGENT["deadline"] is None:
        return None
    return max(AGENT["deadline"] - time.time(), 0)


def report_from(output: str, code: int | str | None) -> str:
    """Return the report a copy printed, or the end of its output without one."""
    if REPORT_MARK in output:
        return output.rsplit(REPORT_MARK, 1)[1].strip() or "(an empty report)"
    return f"(no report; it ended with: {code})\n{output[-1500:].strip()}"


async def spawn(goal: str, context: list[dict]) -> None:
    """/spawn <goal>: deploy a manager, which runs helpers, toward the goal."""
    if PLAN["active"]:
        print("[spawn] plan mode is on: /approve or /cancel it first.")
        return
    if not goal:
        print("[spawn] say the goal: /spawn <goal>")
        return
    minutes = setting("spawn", "max_minutes", DEFAULT_SPAWN_MINUTES)
    deadline = time.time() + 60 * minutes
    run = uuid.uuid4().hex[:8]  # names this run in the trace
    append_trace("spawn", goal=goal, max_minutes=minutes, spawned_run=run)
    print(f"[spawn] manager started with a cut off of {minutes:g} minutes.")

    lines: list[str] = []
    stopped = ""
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as errors:
        manager = await asyncio.create_subprocess_exec(
            *child_command("manager", "manager", goal),
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=errors,
            env={
                **os.environ,
                "HARNESS_DEADLINE": str(deadline),
                "HARNESS_SESSION": SESSION_ID,
                "HARNESS_RUN": run,
                "PYTHONUNBUFFERED": "1",
            },
            start_new_session=True,  # its own group: the whole team can be stopped
            limit=2**20,
        )
        try:
            async with asyncio.timeout(60 * minutes + STOP_GRACE_SECONDS):
                async for raw in manager.stdout:
                    lines.append(raw.decode(errors="replace").rstrip("\n"))
                    if REPORT_MARK not in lines:  # its work, shown as it happens
                        print(f"  {lines[-1]}")
                await manager.wait()
        except TimeoutError:
            stopped = (
                f"[stopped at the time limit: max_minutes {minutes:g} under "
                "spawn in settings.json]\n"
            )
        finally:  # also reached on Ctrl+C: nothing is left running
            with suppress(OSError):
                os.killpg(manager.pid, signal.SIGKILL)

        report = stopped + report_from("\n".join(lines), manager.returncode)
        if REPORT_MARK not in lines:
            errors.seek(0)
            report = f"{report}\n{errors.read()[-1500:].strip()}".strip()
    append_trace("spawn_report", goal=goal, report=report, spawned_run=run)
    print(f"[spawn] the manager's report:\n{report}")
    context.append({"role": "user", "content": f"/spawn {goal}"})
    context.append({"role": "assistant", "content": report})


STOP_GRACE_SECONDS = 5  # the manager stops itself at the limit; then it is stopped


# --------------------------------------------------------------------- loop


# To add a command: write its function above, then add its name here.
# A command is typed in the chat as /name; the model cannot run one.
COMMANDS = [plan, approve, cancel, spawn]

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


def say(text: str) -> str:
    """Print what ends a turn and return it.

    A manager or a helper prints REPORT_MARK first: what follows is its report.
    """
    if AGENT["task"] is not None:
        print(REPORT_MARK)
    print(text, flush=True)
    return text


async def answer(
    context: list[dict],
    tools: list[dict],
    sessions: dict[str, ClientSession],
    deny: set[str],
    model: str | None = None,
) -> str:
    """Call the model until it replies in plain text, running tools between.

    Return what was printed last: the reply, or why there is none. When the
    model cannot be reached, the whole unanswered turn is removed from the
    conversation, so the next prompt starts from a clean state.
    """
    turn_start = len(context) - 1  # the prompt this turn is answering
    max_rounds = setting("model", "max_tool_rounds", DEFAULT_MAX_TOOL_ROUNDS)
    max_chars = setting("tools", "max_output_chars", DEFAULT_MAX_TOOL_OUTPUT_CHARS)

    for _ in range(max_rounds):
        if seconds_left() == 0:
            return say("[harness] stopped at the time limit of this /spawn run.")
        try:
            reply = await in_background(call_model, context, tools, model)
        except GatewayError as error:
            del context[turn_start:]
            hint = f"\n[harness] {error.hint}" if error.hint else ""
            return say(f"[harness] {error}{hint}")

        context.append(reply)
        if not reply.get("tool_calls"):
            fallback = setting(
                "router", "fallback_model", DEFAULT_ROUTER_FALLBACK_MODEL
            )
            if model is None and setting("router", "enabled", False) and fallback:
                numbers = await in_background(
                    judge,
                    context[turn_start]["content"],
                    reply.get("content") or "",
                    context[turn_start + 1 : -1],
                )
                threshold = setting("router", "threshold", DEFAULT_ROUTER_THRESHOLD)
                if numbers is not None:
                    detection, quality = numbers.get("detection"), numbers["quality"]
                    shown = f"[router] judged {quality:.2f}"
                    if len(numbers) > 1:  # every number, quality last
                        others = [f"{name} {numbers[name]:.2f}" for name in numbers if name != "quality"]
                        shown = "[router] judged " + ", ".join(others + [f"quality {quality:.2f}"])
                    # With a question named detection, only a reply that holds code can be sent on.
                    holds_code = detection is None or detection >= ROUTER_DETECTION_CUT
                    if holds_code and quality < threshold:
                        print(f"{shown} < {threshold}: asking {fallback} instead.")
                        del context[turn_start + 1 :]
                        return await answer(
                            context, tools, sessions, deny, model=fallback
                        )
                    print(f"{shown}: keeping the reply.")
            return say(reply.get("content") or "")

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
                f"{' '.join(preview.split())[:PREVIEW_CHARS]}"
            )
            context.append(
                {"role": "tool", "tool_call_id": tool_call["id"], "content": result}
            )

    return say(
        f"[harness] stopped after {max_rounds} rounds of tool calls "
        "(max_tool_rounds under model in settings.json)."
    )


async def main() -> None:
    """Start the servers, then read prompts until the input ends.

    A manager or a helper has no prompt to read: it runs its one task,
    prints its report, and ends.
    """
    role = ROLES.get(AGENT["role"], {"tools": [], "deny": set(), "prompt": None})
    deny = set(setting("permissions", "deny", [])) | role["deny"]
    prompt = role["prompt"] or (
        PROMPT_PATH.read_text(encoding="utf-8")
        if PROMPT_PATH.is_file()
        else DEFAULT_SYSTEM_PROMPT
    )
    LOCAL_FUNCTIONS.update({function.__name__: function for function in role["tools"]})
    role_definitions = [definition(function) for function in role["tools"]]

    async with AsyncExitStack() as stack:
        server_tools, sessions = await start_servers(
            stack, SETTINGS.get("mcpServers", {})
        )
        tools = LOCAL_DEFINITIONS + role_definitions + server_tools
        context = [{"role": "system", "content": prompt + skills_index()}]
        if SKILLS:
            print(f"[skills] {len(SKILLS)} loaded: {', '.join(SKILLS)}")

        if AGENT["task"] is not None:
            context.append({"role": "user", "content": AGENT["task"]})
            await answer(context, tools, sessions, deny)  # ends with its report
            return

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

    # A manager or a helper is started by this program, never by hand.
    parser = argparse.ArgumentParser(description="The harness.")
    parser.add_argument("--role", choices=list(ROLES), help=argparse.SUPPRESS)
    parser.add_argument("--name", help=argparse.SUPPRESS)
    parser.add_argument("--task", help=argparse.SUPPRESS)
    started_as = parser.parse_args()
    if started_as.role:
        AGENT.update(
            name=started_as.name or started_as.role,
            role=started_as.role,
            task=started_as.task or "",
            model=role_model(started_as.role),
            deadline=float(os.environ.get("HARNESS_DEADLINE") or 0) or None,
        )

    with suppress(KeyboardInterrupt):  # Ctrl+C is a normal way to leave
        asyncio.run(main())
    if AGENT["role"] is None:
        print("\n[harness] stopped.")
