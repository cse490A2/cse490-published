"""Test for remember: one line appended to MEMORY.md, and the line count returned."""

from pathlib import Path

from toolcheck import check, numbers, tool

remember = tool("remember", ["text"])

first = remember(text="the build uses ruff")
check(Path("MEMORY.md").is_file(), "remember writes MEMORY.md in the working folder.")
check(numbers(first) == [1.0], "The first call returns 1, the number of lines.", first)

second = remember(text="tests live in tests/")
check(numbers(second) == [2.0], "The second call returns 2.", second)

third = remember(text="two\nparts")
lines = Path("MEMORY.md").read_text(encoding="utf-8").splitlines()
check(
    len(lines) == 3, "Text with a line break in it is still stored as one line.", lines
)
check(numbers(third) == [3.0], "The third call returns 3.", third)
check(
    "the build uses ruff" in lines[0] and "tests live in tests/" in lines[1],
    "Earlier lines are kept, in order.",
    lines,
)

# The read half: the harness gives the notes back to the model at startup.
import harness  # noqa: E402  (toolcheck has put the harness folder on the path)

check(
    callable(getattr(harness, "memory_notes", None)),
    "harness.py has a function memory_notes() that returns the notes for the system prompt.",
)
notes = harness.memory_notes()
check(
    "the build uses ruff" in notes and "tests live in tests/" in notes,
    "memory_notes() returns the lines that remember wrote.",
    notes,
)
source = Path(harness.__file__).read_text(encoding="utf-8")
check(
    source.count("memory_notes(") >= 2,
    "memory_notes() is called where the system prompt is built, not only defined.",
)

# A long file: the newest lines are kept, the oldest are left out, and the notes say so.
Path("MEMORY.md").write_text(
    "".join(f"note {n} " + "x" * 90 + "\n" for n in range(2000)), encoding="utf-8"
)
long_notes = harness.memory_notes()
check(
    len(long_notes) < 100_000,
    "memory_notes() does not return all of a long MEMORY.md.",
    len(long_notes),
)
check("note 1999 " in long_notes, "The newest line of a long file is kept.")
check("note 0 " not in long_notes, "The oldest line of a long file is left out.")
check(
    "MEMORY.md" in long_notes,
    "When lines are left out, the notes name MEMORY.md so the model can read the rest.",
    long_notes[:200],
)
Path("MEMORY.md").unlink()
check(harness.memory_notes() == "", "With no MEMORY.md, memory_notes() returns an empty string.")
print("ok")
