"""Score an answers file from the multi-agent benchmark.

    python tests/score_benchmark.py answers.jsonl

Prints one row per question and the total, then saves a copy of the answers
file outside the harness folder, in p07/answers/, named by the time and the score.
It also reads trace.jsonl for the last /spawn and reports its time, tokens,
cost and tool use, with how often each tool worked. Those numbers are saved
beside the copy, and one row per scored run is added to p07/answers/runs.md.
A later run never replaces it, and no agent can read it. The key beside this file,
benchmark_key.json, holds a fingerprint of each answer and never the answer
itself, so the score can be checked without the answers being readable.

An answer is right when it matches after case, spaces, commas and dollar
signs are dropped. A question with parts (a) to (d) is right when every part
is right and every page it needed is named in "pages"; a list in a part may
be in any order. The last question is the summary. It is right when the
team's own answers to the questions it rests on are right, and the summary
states each of them.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

KEY = json.loads(
    (Path(__file__).resolve().parent / "benchmark_key.json").read_text(encoding="utf-8")
)


def plain(text: object) -> str:
    """Return an answer with case, spaces, commas and dollar signs dropped."""
    return re.sub(r"[\s,$]", "", str(text)).lower()


def fingerprint(number: str, answer: object) -> str:
    """Return the fingerprint the key holds for a right answer."""
    return hashlib.sha256(f"{number}:{plain(answer)}".encode()).hexdigest()


def normal(text: object) -> str:
    """Return one value the way the key was fingerprinted: 6,453.50 becomes 6453.5."""
    text = plain(str(text).strip().strip("[]\"'`").rstrip("."))
    try:
        return f"{float(text):.2f}".rstrip("0").rstrip(".")
    except ValueError:
        return text


def part_fingerprint(label: str, answer: object, is_set: bool) -> str:
    """Return the fingerprint of one part. A set is right in any order."""
    if is_set:
        if isinstance(answer, (list, tuple)):
            answer = ", ".join(str(item) for item in answer)
        items = sorted(normal(item) for item in re.split(r"[,;]|\band\b", str(answer)) if item.strip())
        return hashlib.sha256(f"{label}:{'|'.join(items)}".encode()).hexdigest()
    return hashlib.sha256(f"{label}:{normal(answer)}".encode()).hexdigest()


def score_parts(number: str, rule: dict, item: dict) -> tuple[bool, str]:
    """Score a question with parts. Return whether it is right, and a note.

    It is right when every part is right and every page it needed is named.
    """
    answer = item.get("answer")
    answer = answer if isinstance(answer, dict) else {}
    wrong = [
        label for label, part in rule["answers"].items()
        if part_fingerprint(f"{number}{label}", answer.get(label, ""), part["set"]) != part["is"]
    ]
    cited = item.get("pages")
    cited = cited if isinstance(cited, list) else [item.get("page", "")]
    named = {fingerprint(f"{number}page", Path(str(name)).name) for name in cited}
    missing = sum(1 for page in rule["pages"] if page not in named)
    parts, pages = len(rule["answers"]), len(rule["pages"])
    note = f"parts {parts - len(wrong)} of {parts}"
    if wrong:
        note += f" (wrong: {', '.join(wrong)})"
    note += f", pages named {pages - missing} of {pages} needed"
    return (not wrong and not missing), note


def read_answers(path: Path) -> dict[str, dict]:
    """Return the last readable line for each question number."""
    found: dict[str, dict] = {}
    if not path.is_file():
        return found
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            item = json.loads(line)
            found[str(item["n"])] = item
        except (ValueError, KeyError, TypeError):
            continue
    return found


def stated(summary: str, number: str, answer: object) -> bool:
    """Say whether the summary states an answer. A setting is found by its name."""
    needle = plain(str(answer).split("=")[0])
    if re.fullmatch(r"\d\d:\d\d:\d\d", str(answer).strip()):
        needle = needle[:5]  # a time may be given to the minute
    return bool(needle) and needle in plain(summary)


def main() -> None:
    """Print one row per question and the total."""
    if len(sys.argv) != 2:
        sys.exit("usage: python tests/score_benchmark.py answers.jsonl")
    answers_file = Path(sys.argv[1])
    given = read_answers(answers_file)
    right: dict[str, bool] = {}
    for number, key in KEY["answers"].items():
        answer = given.get(number, {}).get("answer", "(none)")
        right[number] = fingerprint(number, answer) == key
        print(f"{number:>2}  {'right' if right[number] else 'WRONG':<5}  {str(answer)[:40]}")

    for number, rule in KEY.get("parts", {}).items():
        right[number], note = score_parts(number, rule, given.get(number, {}))
        print(f"{number:>2}  {'right' if right[number] else 'WRONG':<5}  {note}")

    number, rests_on = KEY["summary"]["n"], KEY["summary"]["rests_on"]
    summary = str(given.get(number, {}).get("answer", ""))
    held = [
        n for n in rests_on
        if right[n] and stated(summary, n, given[n]["answer"])
    ]
    right[number] = len(held) == len(rests_on)
    missing = [n for n in rests_on if n not in held]
    note = "" if right[number] else f"  (not stated, or wrong: questions {', '.join(missing)})"
    print(f"{number:>2}  {'right' if right[number] else 'WRONG':<5}  "
          f"summary states {len(held)} of {len(rests_on)} answers{note}")
    print(f"{sum(right.values())} of {len(right)} right")
    run = run_numbers()
    print_run(run)
    keep_copy(answers_file, sum(right.values()), len(right), run)


HARNESS = Path(__file__).resolve().parent.parent


def failed(reply: object) -> bool:
    """True when a tool's reply reports a failure."""
    text = str(reply).lstrip()
    return text.startswith("Error") or "isError': True" in text[:40] or 'isError": true' in text[:40]


def moment(line: dict) -> float | None:
    """A trace line's time, in seconds, or None when it has none."""
    try:
        return datetime.fromisoformat(str(line["time"]).replace("Z", "+00:00")).timestamp()
    except (KeyError, ValueError):
        return None


def run_numbers() -> dict | None:
    """Time, tokens, cost and tool use of the last /spawn in trace.jsonl, or None."""
    trace = HARNESS / "trace.jsonl"
    if not trace.is_file():
        return None
    lines = []
    for text in trace.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            lines.append(json.loads(text))
        except ValueError:
            continue
    starts = [i for i, line in enumerate(lines) if line.get("type") == "spawn"]
    if not starts:
        return None
    lines = lines[starts[-1]:]
    ends = [i for i, line in enumerate(lines) if line.get("type") == "spawn_report"]
    finished = bool(ends)
    if finished:
        lines = lines[: ends[0] + 1]
    times = [m for m in map(moment, lines) if m is not None]
    calls = [line for line in lines if line.get("type") == "model_call"]
    tokens = [line.get("tokens") or {} for line in calls]
    tools: dict[str, dict[str, int]] = {}
    for line in lines:
        if line.get("type") not in ("tool_call", "tool_reply"):
            continue
        row = tools.setdefault(str(line.get("name")), {"calls": 0, "failed": 0})
        if line["type"] == "tool_call":
            row["calls"] += 1
        elif failed(line.get("reply")):
            row["failed"] += 1
    return {
        "finished": finished,
        "minutes": round((max(times) - min(times)) / 60, 1) if times else None,
        "helpers": sum(1 for line in lines if line.get("type") == "helper_start"),
        "model_calls": len(calls),
        "tokens_in": sum(t.get("prompt") or 0 for t in tokens),
        "tokens_out": sum(t.get("completion") or 0 for t in tokens),
        "cost": round(sum(line.get("spend") or 0 for line in calls), 4),
        "tool_calls": sum(row["calls"] for row in tools.values()),
        "tool_failures": sum(row["failed"] for row in tools.values()),
        "tools": tools,
    }


def print_run(run: dict | None) -> None:
    """Print the run's numbers under the score."""
    if run is None:
        print("no /spawn found in trace.jsonl, so there are no run numbers")
        return
    print()
    print("the last /spawn in trace.jsonl" + ("" if run["finished"] else " (it did not finish)"))
    print(f"  time     {run['minutes']} min, {run['helpers']} helpers started")
    print(f"  tokens   {run['tokens_in']:,} in, {run['tokens_out']:,} out, "
          f"{run['model_calls']} model calls")
    print(f"  cost     ${run['cost']:.2f}")
    print(f"  tools    {run['tool_calls']} calls, {run['tool_failures']} failed")
    for name, row in sorted(run["tools"].items(), key=lambda item: -item[1]["calls"]):
        worked = row["calls"] - row["failed"]
        rate = round(100 * worked / row["calls"]) if row["calls"] else 0
        print(f"    {name:<16}{row['calls']:>4} calls  {worked:>4} worked  {rate:>3}%")


def keep_copy(answers_file: Path, right: int, total: int, run: dict | None) -> None:
    """Save the scored file and its numbers outside the harness folder."""
    score = f"{right}of{total}"
    harness = HARNESS
    beside = harness.parent
    folder = beside / "p07" / "answers" if (beside / "p07").is_dir() else beside / "p07_answers"
    if not answers_file.is_file():
        print(f"no file named {answers_file}: nothing was scored, and no copy was saved")
        return
    if answers_file.resolve().parent == folder.resolve():
        return  # this is a saved copy being scored again
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{answers_file.stem}-{time.strftime('%H%M%S')}-{score}"
    copy = folder / f"{name}.jsonl"
    shutil.copyfile(answers_file, copy)
    record = {"file": copy.name, "right": right, "of": total, "run": run}
    (folder / f"{name}.run.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    table = folder / "runs.md"
    if not table.is_file():
        table.write_text(
            "| saved file | score | minutes | helpers | tokens in | tokens out | cost | "
            "tool calls | failed |\n|---|---|---|---|---|---|---|---|---|\n",
            encoding="utf-8",
        )
    r = run or {}
    cost = f"${r['cost']:.2f}" if r else "-"
    row = [copy.name, f"{right} of {total}", r.get("minutes", "-"), r.get("helpers", "-"),
           r.get("tokens_in", "-"), r.get("tokens_out", "-"), cost,
           r.get("tool_calls", "-"), r.get("tool_failures", "-")]
    with table.open("a", encoding="utf-8") as file:
        file.write("| " + " | ".join(str(cell) for cell in row) + " |\n")
    print()
    print(f"saved a copy: {copy}")
    print(f"every scored run, side by side: {table}")


if __name__ == "__main__":
    main()
