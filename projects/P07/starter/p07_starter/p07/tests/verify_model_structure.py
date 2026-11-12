"""Check that a harness has what Project 7 builds on.

    python p07/tests/verify_model_structure.py              # the harness beside p07
    python p07/tests/verify_model_structure.py path/to/harness

Run it with the harness's own Python (.venv-harness on), from p07_starter.
It prints one row per check and, for each one that fails, what to change.
It ends with "ready" and exits with 0 when every check passes. It reads the
harness and never changes it, and it never calls the model.
"""

from __future__ import annotations

import inspect
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS: list[tuple[bool, str, str]] = []


def find_harness() -> Path:
    """Return the harness folder: the one named, or the one beside p07."""
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    for folder in (HERE.parent, HERE.parent.parent / "harness"):
        if (folder / "harness.py").is_file():
            return folder
    return HERE.parent.parent / "harness"


def check(passed: object, what: str, fix: str) -> bool:
    """Record one check: what was looked for, and what to change when it failed."""
    ROWS.append((bool(passed), what, fix))
    return bool(passed)


def finish() -> None:
    """Print every row and the verdict, then exit."""
    for passed, what, fix in ROWS:
        print(f"{'ok     ' if passed else 'MISSING'}  {what}")
        if not passed:
            print(f"         {fix}")
    failed = sum(not passed for passed, _, _ in ROWS)
    print()
    print(
        "ready" if not failed else f"not ready: {failed} of {len(ROWS)} checks failed"
    )
    sys.exit(1 if failed else 0)


def check_settings(home: Path) -> None:
    """settings.json is there, is one object, and names an MCP server."""
    path = home / "settings.json"
    if not check(
        path.is_file(),
        "settings.json beside harness.py",
        "Make settings.json in the harness folder. Project 6's setup has its contents.",
    ):
        return
    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        check(False, "settings.json is valid JSON", f"Mend the file: {error}")
        return
    check(
        isinstance(settings, dict),
        "settings.json is one object: { ... }",
        "Wrap the settings in one pair of braces.",
    )
    servers = settings.get("mcpServers") if isinstance(settings, dict) else None
    check(
        isinstance(servers, dict) and servers,
        "settings.json names an MCP server (server tools)",
        'Add the "mcpServers" section with the GitHub server, as in Project 6.',
    )


def load(home: Path) -> object | None:
    """Import harness.py from the folder, or record why it would not load."""
    if not check(
        (home / "harness.py").is_file(),
        f"harness.py in {home}",
        "Name the harness folder as the argument: verify_model_structure.py path/to/harness",
    ):
        return None
    source = (home / "harness.py").read_text(encoding="utf-8")
    if not check(
        "__name__" in source and "__main__" in source,
        "harness.py can be imported without starting",
        "It starts as soon as it is imported, so no test can load it. Put the line that "
        'starts it under: if __name__ == "__main__":',
    ):
        return None
    sys.path.insert(0, str(home))
    try:
        import harness
    except ImportError as error:
        check(
            False,
            "harness.py loads",
            f"{error}. Turn on .venv-harness and run this again, or install the "
            "missing package into that environment.",
        )
        return None
    except BaseException as error:  # noqa: BLE001  (a student's harness may fail in any way)
        check(
            False,
            "harness.py loads",
            f"It stopped with {type(error).__name__}: {error}",
        )
        return None
    check(True, "harness.py loads", "")
    return harness


def check_names(harness: object) -> bool:
    """The six names are there, each of the right kind."""
    before = len(ROWS)
    tools = getattr(harness, "LOCAL_TOOLS", None)
    listed = check(
        isinstance(tools, list) and tools and all(callable(tool) for tool in tools),
        "LOCAL_TOOLS is a list of your tool functions",
        "Put the tool functions in one list: LOCAL_TOOLS = [read_file, write_file, ...]",
    )
    functions = getattr(harness, "LOCAL_FUNCTIONS", None)
    looked_up = check(
        isinstance(functions, dict)
        and functions
        and all(callable(f) for f in functions.values()),
        "LOCAL_FUNCTIONS looks the same tools up by name",
        "Add: LOCAL_FUNCTIONS = {function.__name__: function for function in LOCAL_TOOLS}",
    )
    if listed and looked_up:
        check(
            set(functions) == {tool.__name__ for tool in tools},
            "LOCAL_FUNCTIONS and LOCAL_TOOLS hold the same tools",
            "Build LOCAL_FUNCTIONS from LOCAL_TOOLS, so the two cannot differ.",
        )
    for name, arguments, fix in (
        (
            "run_local_tool",
            2,
            "Add run_local_tool(name, args): it runs one tool and returns its result as text.",
        ),
        (
            "definition",
            1,
            "Add definition(function): it builds what the model is told about a tool.",
        ),
        (
            "checked",
            1,
            "Add checked(path): it returns the path, and refuses one outside the folder or .env.",
        ),
        (
            "call_model",
            2,
            "Add call_model(context, tools): it sends the conversation and returns the model's message.",
        ),
    ):
        function = getattr(harness, name, None)
        takes = (
            len(inspect.signature(function).parameters) if callable(function) else -1
        )
        check(
            takes == arguments,
            f"{name} takes {arguments} argument{'s' if arguments > 1 else ''}",
            fix,
        )
    return all(passed for passed, _, _ in ROWS[before:])


def check_tools(harness: object) -> None:
    """The three local tools are there, and described for the model."""
    functions = harness.LOCAL_FUNCTIONS
    check(
        "read_file" in functions,
        "a read_file tool",
        "Add read_file(path) to LOCAL_TOOLS.",
    )
    check(
        "write_file" in functions,
        "a write_file tool",
        "Add write_file(path, content) to LOCAL_TOOLS.",
    )
    check(
        "execute" in functions or "execute_file" in functions,
        "an execute tool, named execute or execute_file",
        "Add a tool that runs a Python file and returns its output.",
    )
    if "read_file" not in functions:
        return
    try:
        described = harness.definition(functions["read_file"])["function"]
        shape = (
            described["name"] == "read_file"
            and described["description"]
            and "path" in described["parameters"]["properties"]
        )
    except Exception:  # noqa: BLE001  (any other shape is a failed check)
        shape = False
    check(
        shape,
        "definition(read_file) gives a name, a description and the path argument",
        'Return {"type": "function", "function": {"name", "description", "parameters"}}, '
        "and give read_file a docstring.",
    )


def check_behaviour(harness: object) -> None:
    """checked refuses what it must, and a failing tool answers with Error."""
    start = Path.cwd()
    with tempfile.TemporaryDirectory() as folder:
        os.chdir(folder)
        try:
            Path("inside.txt").write_text("x", encoding="utf-8")
            try:
                inside = Path(harness.checked("inside.txt")).name == "inside.txt"
            except Exception:  # noqa: BLE001
                inside = False
            check(
                inside,
                "checked accepts a path inside the working folder",
                "checked(path) returns the path when it is inside the folder the harness runs in.",
            )
            for path, what in (
                ("../outside.txt", "a path outside the working folder"),
                (".env", ".env"),
            ):
                try:
                    harness.checked(path)
                    refused = False
                except Exception:  # noqa: BLE001
                    refused = True
                check(
                    refused,
                    f"checked refuses {what}",
                    f"checked({path!r}) must raise an error.",
                )
            if "read_file" in harness.LOCAL_FUNCTIONS:
                try:
                    answer = harness.run_local_tool(
                        "read_file", {"path": "no_such_file.txt"}
                    )
                except Exception as error:  # noqa: BLE001
                    answer = f"(it raised {type(error).__name__})"
                check(
                    isinstance(answer, str) and answer.startswith("Error"),
                    "a tool that fails answers with text that starts with Error",
                    f"run_local_tool must catch the tool's error and return 'Error: ...'. It gave: {answer!r}",
                )
        finally:
            os.chdir(start)


def main() -> None:
    """Run every check that can run, and print the result."""
    home = find_harness()
    print(f"Checking the harness in {home}\n")
    check_settings(home)
    harness = load(home)
    if harness is not None and check_names(harness):
        check_tools(harness)
        check_behaviour(harness)
    finish()


if __name__ == "__main__":
    main()
