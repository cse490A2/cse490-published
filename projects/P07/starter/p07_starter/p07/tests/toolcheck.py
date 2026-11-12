"""Shared by every test_<tool>.py: find the harness, work in an empty folder.

Each test is a plain script. It prints "ok" and exits with 0 when the tool
does what upgrade_spec/TOOLS.md says, or prints one FAIL line and exits with 1.

A test never touches the project's own files. Importing this module moves the
script into a new, empty folder, and that folder is removed at the end.
"""

from __future__ import annotations

import atexit
import os
import re
import shutil
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

HERE = Path(__file__).resolve().parent

# tests/ sits beside harness.py. Before it is moved there it sits in p07/,
# and the harness folder is beside p07/.
HOME = next(
    (
        folder
        for folder in (HERE.parent, HERE.parent.parent / "harness")
        if (folder / "harness.py").is_file()
    ),
    None,
)
if HOME is None:
    sys.exit("FAIL: no harness.py found. Put the tests folder beside harness.py.")

sys.path.insert(0, str(HOME))
import harness

WORK = Path(tempfile.mkdtemp(prefix="tooltest-")).resolve()
os.chdir(WORK)


@atexit.register
def remove_work_folder() -> None:
    """Leave the temporary folder, then delete it."""
    os.chdir(HOME)
    shutil.rmtree(WORK, ignore_errors=True)


def check(passed: object, wanted: str, got: object = None) -> None:
    """Stop the test with one FAIL line when the condition does not hold."""
    if passed:
        return
    line = f"FAIL {Path(sys.argv[0]).name}: {wanted}"
    if got is not None:
        line += f"\n  got: {str(got)[:400]!r}"
    print(line)
    sys.exit(1)


def tool(name: str, arguments: list[str]) -> Callable[..., str]:
    """Return the tool as the model calls it, after checking how it is listed.

    The tool has to be in LOCAL_TOOLS, describe itself in its docstring, and
    take the arguments TOOLS.md gives it.
    """
    check(
        name in harness.LOCAL_FUNCTIONS,
        f"{name} is not in LOCAL_TOOLS. Write the function, then add its name "
        "to the list.",
    )
    listed = harness.definition(harness.LOCAL_FUNCTIONS[name])["function"]
    check(listed["description"], f"{name} has no docstring for the model to read.")
    check(
        list(listed["parameters"]["properties"]) == arguments,
        f"{name} takes the arguments {arguments}.",
        list(listed["parameters"]["properties"]),
    )
    return lambda **given: harness.run_local_tool(name, given)


def numbers(text: str) -> list[float]:
    """Return every number in the text. A comma inside a number is dropped."""
    return [
        float(found) for found in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))
    ]


def is_error(result: str) -> bool:
    """Say whether a tool's result is an error, as the rules in TOOLS.md put it."""
    return result.startswith("Error")
