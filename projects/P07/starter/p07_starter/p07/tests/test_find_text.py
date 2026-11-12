"""Test for find_text: every match as path:line: text, with the skips and the limits."""

from pathlib import Path

from toolcheck import check, tool

Path("notes.txt").write_text("first line\nthe needle is here\n", encoding="utf-8")
Path("src").mkdir()
Path("src/app.py").write_text("x = 1\ny = 2\nneedle = 3\n", encoding="utf-8")
Path("wide.txt").write_text("needle " + "w" * 900 + "\n", encoding="utf-8")
Path("trace.jsonl").write_text('{"text": "needle"}\n', encoding="utf-8")
for hidden in (".undo", ".git"):
    Path(hidden).mkdir()
    Path(hidden, "copy.txt").write_text("needle\n", encoding="utf-8")

find_text = tool("find_text", ["text"])
lines = find_text(text="needle").replace("\\", "/").splitlines()

check(
    "notes.txt:2: the needle is here" in lines, "A match reads path:line: text.", lines
)
check("src/app.py:3: needle = 3" in lines, "Files in folders are searched.", lines)
check(
    not any("trace.jsonl" in line for line in lines), "trace.jsonl is skipped.", lines
)
check(not any(".undo" in line for line in lines), "The .undo folder is skipped.", lines)
check(
    not any(".git" in line for line in lines),
    "A folder whose name starts with a dot is skipped.",
    lines,
)
wide = [line for line in lines if line.startswith("wide.txt:1:")]
check(
    len(wide) == 1 and len(wide[0]) <= len("wide.txt:1: ") + 300,
    "A line is cut at 300 characters.",
    [len(line) for line in wide],
)

Path("many.txt").write_text("needle\n" * 250, encoding="utf-8")
many = [line for line in find_text(text="needle").splitlines() if ":" in line]
check(len(many) <= 200, "The search stops at 200 matches.", len(many))
check(len(many) >= 150, "It returns matches up to that limit.", len(many))
print("ok")
