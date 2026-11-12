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
print("ok")
