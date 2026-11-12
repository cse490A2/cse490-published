"""Test for todo: todo.md is written as a checklist, and the checklist is returned."""

from pathlib import Path

from toolcheck import check, tool

todo = tool("todo", ["items"])

result = todo(items="[x] read the spec\nwrite the tool\nrun the test")
check(Path("todo.md").is_file(), "todo writes todo.md in the working folder.")
written = Path("todo.md").read_text(encoding="utf-8")
lines = written.splitlines()

check(result.strip() == written.strip(), "todo returns what it wrote.", result)
check(len(lines) == 3, "One line of todo.md per item.", lines)
check("[x] read the spec" in lines[0], "A line that starts with [x] is done.", lines)
check("[ ] write the tool" in lines[1], "Any other line is open: [ ].", lines)
check("[ ] run the test" in lines[2], "Any other line is open: [ ].", lines)

todo(items="[x] read the spec\n[x] write the tool")
again = Path("todo.md").read_text(encoding="utf-8").splitlines()
check(len(again) == 2, "A new call replaces the list. It never adds to it.", again)
check("[x] write the tool" in again[1], "The new list is the one on disk.", again)
print("ok")
