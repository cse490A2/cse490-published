"""Test for undo: write_file keeps a copy under .undo/, and undo puts it back."""

from pathlib import Path

from toolcheck import check, is_error, tool

undo = tool("undo", ["path"])
write_file = tool("write_file", ["path", "content"])

write_file(path="notes.txt", content="one")
check(
    not Path(".undo/notes.txt").exists(),
    "A file that did not exist has no copy under .undo/.",
)
none_yet = undo(path="notes.txt")
check(is_error(none_yet), "undo with no copy returns Error: ...", none_yet)

write_file(path="notes.txt", content="two")
check(
    Path(".undo/notes.txt").is_file()
    and Path(".undo/notes.txt").read_text(encoding="utf-8") == "one",
    "write_file copies the file to .undo/<the same path> before it writes.",
)

restored = undo(path="notes.txt")
check(not is_error(restored), "undo puts the file back.", restored)
check("notes.txt" in restored, "undo returns the path it restored.", restored)
check(
    Path("notes.txt").read_text(encoding="utf-8") == "one",
    "After undo the file holds what it held before the last write.",
    Path("notes.txt").read_text(encoding="utf-8"),
)

Path("src").mkdir()
write_file(path="src/app.py", content="x = 1\n")
write_file(path="src/app.py", content="x = 2\n")
check(
    Path(".undo/src/app.py").is_file(),
    "A file in a folder is copied to the same path under .undo/.",
)
undo(path="src/app.py")
check(
    Path("src/app.py").read_text(encoding="utf-8") == "x = 1\n",
    "undo works on a file in a folder.",
)

outside = undo(path="../elsewhere.txt")
check(is_error(outside), "A path outside the working folder is refused.", outside)
print("ok")
