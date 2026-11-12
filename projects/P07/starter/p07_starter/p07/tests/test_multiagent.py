"""Test for /spawn: the team your harness starts, as upgrade_spec/SPAWN.md describes it.

    python tests/test_multiagent.py

Run it by hand, with .venv-harness on. It takes about a minute and makes a
few real calls to the model, so it needs the key in .env and, off campus, the
UW VPN. It prints one line per check, then "ok" and exits with 0, or one FAIL
line and exits with 1.

How it works: it copies your harness into an empty temporary folder, starts
it there as a separate program, types /spawn into it, and reads what the run
left behind: the files, the lines of trace.jsonl, and the programs still
running. Your own folder and your own trace are never touched.
"""

from __future__ import annotations

import atexit
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOME = next(
    (
        folder
        for folder in (HERE.parent, HERE.parent.parent / "harness")
        if (folder / "harness.py").is_file()
    ),
    None,
)
GOAL = (
    "write the numbers one to three into one.txt, two.txt and three.txt, "
    "one file per helper: one.txt holds 1, two.txt holds 2, three.txt holds 3"
)
LONG_GOAL = "write a 300 word story into each of ten files, story-1.txt to story-10.txt"
FOLDERS: list[Path] = []  # every temporary copy made, removed when the test ends


@atexit.register
def remove_folders() -> None:
    """Delete the temporary copies, whether the test passed or not."""
    for folder in FOLDERS:
        shutil.rmtree(folder, ignore_errors=True)


def fail(wanted: str, got: object = None) -> None:
    """Stop the test with one FAIL line."""
    line = f"FAIL {Path(sys.argv[0]).name}: {wanted}"
    if got is not None:
        line += f"\n  got: {str(got)[-500:]!r}"
    print(line)
    sys.exit(1)


def check(passed: object, wanted: str, got: object = None) -> None:
    """Print the check when it holds. Stop the test when it does not."""
    if not passed:
        fail(wanted, got)
    print(f"ok    {wanted}")


def fresh_copy(spawn: dict) -> Path:
    """Copy the harness into a new empty folder, with the spawn settings given."""
    work = Path(tempfile.mkdtemp(prefix="spawntest-")).resolve()
    FOLDERS.append(work)
    for name in ("harness.py", "trace.py", ".env", "systemprompt.md"):
        if (HOME / name).is_file():
            shutil.copy(HOME / name, work / name)
    settings = {}
    if (HOME / "settings.json").is_file():
        settings = json.loads((HOME / "settings.json").read_text(encoding="utf-8"))
    settings.pop("mcpServers", None)  # the test needs no server tools
    settings["spawn"] = {**settings.get("spawn", {}), **spawn}
    (work / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    return work


def run(
    work: Path, arguments: list[str], typed: str, limit: float
) -> tuple[str, float]:
    """Start the harness in a folder, type into it, and return its output and seconds."""
    started = time.time()
    try:
        done = subprocess.run(
            [sys.executable, "harness.py", *arguments],
            cwd=work,
            input=typed,
            capture_output=True,
            text=True,
            timeout=limit,
            check=False,
        )
        output = done.stdout + done.stderr
    except subprocess.TimeoutExpired as late:
        output = f"(still running after {limit:g} seconds) {late.stdout or ''}"
    return output, time.time() - started


def trace(work: Path) -> list[dict]:
    """Return the lines of the folder's trace.jsonl."""
    path = work / "trace.jsonl"
    if not path.is_file():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def still_running(work: Path) -> list[str]:
    """Return the harness programs still running from a folder."""
    listed = subprocess.run(
        ["ps", "-ax", "-o", "pid=,command="],
        capture_output=True,
        text=True,
        check=False,
    )
    return [
        line.strip()
        for line in listed.stdout.splitlines()
        if str(work) in line and "harness.py" in line
    ]


def no_model_checks() -> None:
    """What can be checked without the model: the usage line and the helper limit."""
    work = fresh_copy({"max_helpers": 2, "max_minutes": 1})
    listed = subprocess.run(
        [
            sys.executable,
            "-c",
            "import harness; print([c.__name__ for c in harness.COMMANDS])",
        ],
        cwd=work,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    check(
        "'spawn'" in listed.stdout,
        "spawn is in the COMMANDS list of harness.py",
        listed.stdout + listed.stderr,
    )
    output, seconds = run(work, [], "/spawn\n", 30)
    check(
        "/spawn" in output and seconds < 20,
        "/spawn with no goal says how to use it",
        output,
    )
    kinds = [line.get("type") for line in trace(work)]
    check(
        "helper_start" not in kinds and "spawn" not in kinds,
        "/spawn with no goal starts nothing",
        kinds,
    )

    probe = (
        "import harness, json\n"
        "print(json.dumps({'chat_has_it': 'start_helpers' in harness.LOCAL_FUNCTIONS,\n"
        "                  'answer': str(harness.start_helpers(['a', 'b', 'c']))}))\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=work,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    try:
        told = json.loads(done.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        fail(
            "harness.py has a start_helpers(tasks) function that can be called",
            done.stdout + done.stderr,
        )
    check(
        not told["chat_has_it"],
        "the chat does not have start_helpers: only the manager does",
    )
    check(
        told["answer"].startswith("refused") and "max_helpers" in told["answer"],
        "3 helpers with max_helpers 2 is refused, and the answer names max_helpers",
        told["answer"],
    )
    check(
        not still_running(work), "a refused call starts no helper", still_running(work)
    )


def one_copy_check() -> None:
    """A copy started with --role and --task runs its task and prints its report."""
    work = fresh_copy({"max_minutes": 1})
    output, _ = run(
        work,
        [
            "--role",
            "helper",
            "--name",
            "helper-test",
            "--task",
            "Reply with the single word ready.",
        ],
        "",
        90,
    )
    mark = "=== report ==="
    check(
        mark in output,
        "a copy started with --role helper --task prints the line === report ===",
        output,
    )
    check(output.rsplit(mark, 1)[1].strip(), "its report follows that line", output)


def team_check() -> None:
    """One real /spawn: the files are made, and the trace shows a team did it."""
    work = fresh_copy({"max_helpers": 8, "max_minutes": 3})
    output, _ = run(work, [], f"/spawn {GOAL}\n", 240)
    made = {
        name: (work / name).is_file() for name in ("one.txt", "two.txt", "three.txt")
    }
    check(
        all(made.values()),
        "/spawn with a goal for three helpers makes the three files",
        [made, output],
    )
    lines = trace(work)
    kinds = [line.get("type") for line in lines]
    for kind in ("spawn", "helper_start", "helper_report", "spawn_report"):
        check(kind in kinds, f"the trace has a {kind} line", sorted(set(kinds)))
    spans: dict[str, list[str]] = {}  # each helper's first and last moment in the trace
    for line in lines:
        name = str(line.get("agent"))
        if name.startswith("helper-") and isinstance(line.get("time"), str):
            spans.setdefault(name, []).append(line["time"])
    ranges = sorted((min(times), max(times)) for times in spans.values())
    overlap = any(later[0] < earlier[1] for earlier, later in itertools.pairwise(ranges))
    check(
        overlap,
        "the helpers work at the same moment: one starts before another has finished. "
        "Start every helper first, and wait for them second",
        ranges,
    )
    agents = {line.get("agent") for line in lines}
    check(
        "manager" in agents and any(str(a).startswith("helper-") for a in agents),
        "trace lines carry the agent's name: manager, helper-1, ...",
        sorted(str(a) for a in agents),
    )
    sessions = {
        json.dumps(line.get("session"), sort_keys=True)
        for line in lines
        if line.get("type") == "tool_call"
    }
    check(
        len(sessions) == 1,
        "every agent writes under the one session of the chat that typed /spawn",
        len(sessions),
    )
    wrote = [
        line
        for line in lines
        if line.get("type") == "tool_call"
        and line.get("agent") == "manager"
        and line.get("name") == "write_file"
    ]
    check(not wrote, "the manager wrote no file itself: a helper did")
    check(
        not still_running(work),
        "nothing is left running after the run",
        still_running(work),
    )


def time_limit_check() -> None:
    """max_minutes stops the whole team, and leaves nothing running."""
    work = fresh_copy({"max_helpers": 8, "max_minutes": 0.2})  # twelve seconds
    output, seconds = run(work, [], f"/spawn {LONG_GOAL}\n", 90)
    check(
        seconds < 45,
        "with max_minutes 0.2 a long goal is stopped in well under a minute",
        f"{seconds:.0f} s",
    )
    check(
        "time limit" in output or "max_minutes" in output,
        "the report says the run stopped at the time limit",
        output,
    )
    time.sleep(2)
    check(
        not still_running(work),
        "no harness.py is left running after the time limit",
        still_running(work),
    )


def main() -> None:
    """Run the checks, cheapest first."""
    if HOME is None:
        fail("no harness.py found. Put the tests folder beside harness.py.")
    if not (HOME / ".env").is_file():
        fail(".env beside harness.py: the test makes real calls to the model.")
    print(f"Testing /spawn in {HOME} (about a minute)\n")
    no_model_checks()
    one_copy_check()
    team_check()
    time_limit_check()
    print("\nok")


if __name__ == "__main__":
    main()
