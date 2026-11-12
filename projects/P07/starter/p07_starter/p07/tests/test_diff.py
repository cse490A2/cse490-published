"""Test for diff: a unified diff of a file against its copy under .undo/."""

from toolcheck import check, is_error, tool

diff = tool("diff", ["path"])
write_file = tool("write_file", ["path", "content"])

write_file(path="notes.txt", content="alpha\nbravo\ncharlie\n")
none_yet = diff(path="notes.txt")
check(is_error(none_yet), "diff with no copy under .undo/ returns Error: ...", none_yet)

write_file(path="notes.txt", content="alpha\nBRAVO\ncharlie\n")
result = diff(path="notes.txt")
lines = result.splitlines()

check(not is_error(result), "diff compares the file with its copy.", result)
check(
    any(line.startswith("---") for line in lines)
    and any(line.startswith("+++") for line in lines)
    and any(line.startswith("@@") for line in lines),
    "The result is a unified diff: ---, +++ and @@ lines.",
    result,
)
check("-bravo" in lines, "The line that was replaced is marked with -.", result)
check("+BRAVO" in lines, "The line that replaced it is marked with +.", result)
check(
    lines.index("-bravo") < lines.index("+BRAVO"),
    "The copy under .undo/ is the old side, and the file is the new side.",
    result,
)

outside = diff(path="../elsewhere.txt")
check(is_error(outside), "A path outside the working folder is refused.", outside)
print("ok")
