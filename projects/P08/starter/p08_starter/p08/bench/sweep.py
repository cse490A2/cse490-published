"""
Show what each threshold would send to the stronger model.

run, from your harness folder (the decider server must be running):
    source .venv-harness/bin/activate
    python bench/sweep.py
    python bench/sweep.py --only 1,11,21    just these responses

bench/responses.jsonl holds 30 responses Qwen gave earlier, each with the
prompt it answered:
    10  no code            answers to multiple-choice questions
    10  code that passed   the problem's tests ran on it and passed
    10  code that failed   the problem's tests ran on it and failed

Your router's own judge() reads each one, with your questions from
settings.json and your decider. No model answers anything here: Qwen and Haiku
are not called, so the gateway and the VPN are not needed.

A response goes to the stronger model when detection is at least 0.5 and
quality is below the threshold. For each threshold from 0.1 to 0.9 the table
counts how many of each kind would go: the failed code you want sent, and the
passed code and the no-code answers that would go with it. The table is saved
to bench/sweep.txt.

The judgments are recorded in bench/runs/trace.jsonl, so your own trace.jsonl
is left alone.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent  # harness/bench
HARNESS = HERE.parent  # harness: harness.py, settings.json
sys.path.insert(0, str(HARNESS))
import harness  # noqa: E402

RESPONSES_PATH = HERE / "responses.jsonl"
TABLE_PATH = HERE / "sweep.txt"
RUNS = HERE / "runs"
THRESHOLDS = [round(0.1 * step, 1) for step in range(1, 10)]
DETECTION_CUT = 0.5  # detection at or above this: the response holds program code
KINDS = ["code failed", "code passed", "no code"]
STEP_ONE = "Do the handout's step 1 first."


def read_responses(only: set[int] | None) -> list[dict]:
    """Return the rows of responses.jsonl, or just the chosen ids."""
    lines = RESPONSES_PATH.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    for row in rows:
        if row.get("kind") not in KINDS:
            sys.exit(f"response {row.get('id')}: kind must be one of {', '.join(KINDS)}")
    return [row for row in rows if not only or row["id"] in only]


def judged(row: dict) -> tuple[dict | None, str]:
    """Return your router's two numbers for one saved response, and what it printed."""
    shown = io.StringIO()
    with contextlib.redirect_stdout(shown):  # keep the router's own prints out of the table
        numbers = harness.judge(row["prompt"], row["response"], [])
    said = " ".join(shown.getvalue().split())
    if numbers is None:
        return None, said
    if not isinstance(numbers, dict) or "detection" not in numbers:
        sys.exit(f"\nYour router returned no detection number: it still asks one question. {STEP_ONE}")
    return {"detection": float(numbers["detection"]), "quality": float(numbers["quality"])}, said


def sent(numbers: dict, threshold: float) -> bool:
    """Return True when the router would send this response to the stronger model."""
    return numbers["detection"] >= DETECTION_CUT and numbers["quality"] < threshold


def asked(name: str) -> str:
    """Return the wording of one of the router's questions in settings.json."""
    questions = harness.setting("router", "questions", {})
    entry = questions.get(name) if isinstance(questions, dict) else None
    return entry.get("question", "") if isinstance(entry, dict) else ""


def row_text(result: dict) -> str:
    """Return one line of progress for one response."""
    numbers = result["numbers"]
    head = f"{result['id']:>3}  {result['kind']:11}"
    if numbers is None:
        return f"{head}  no numbers: {result['said'][:90]}"
    return f"{head}  detection {numbers['detection']:.2f}  quality {numbers['quality']:.2f}"


def table(results: list[dict]) -> str:
    """Return the count at each threshold, then what was asked and how detection did."""
    have = [r for r in results if r["numbers"] is not None]
    of = {kind: sum(r["kind"] == kind for r in have) for kind in KINDS}
    lines = [
        "threshold  failed code sent  passed code sent  no-code sent  Haiku calls  failed minus good",
    ]
    best = None  # (score, threshold): the first largest score, so a tie takes the lower threshold
    for threshold in THRESHOLDS:
        gone = [r for r in have if sent(r["numbers"], threshold)]
        count = {kind: sum(r["kind"] == kind for r in gone) for kind in KINDS}
        # failed code sent, minus every response sent that did not need to be
        score = count["code failed"] - count["code passed"] - count["no code"]
        if best is None or score > best[0]:
            best = (score, threshold)
        lines.append(
            f"{threshold:9.1f}  {count['code failed']:>9} of {of['code failed']:<3}"
            f"  {count['code passed']:>9} of {of['code passed']:<3}"
            f"  {count['no code']:>5} of {of['no code']:<3}  {len(gone):>11}  {score:>17}"
        )
    lines += [
        "",
        f"best threshold: {best[1]:.1f}  (failed minus good is largest there; a tie takes the lower threshold)",
        "failed minus good: failed code sent, minus passed code sent and no-code sent",
        f"detection question: {asked('detection')}",
        f"quality question: {asked('quality')}",
        f"rule: send when detection >= {DETECTION_CUT} and quality < threshold",
        "detection at 0.5 or above: "
        + ", ".join(
            f"{sum(r['numbers']['detection'] >= DETECTION_CUT for r in have if r['kind'] == kind)}"
            f" of {of[kind]} {kind}"
            for kind in KINDS
        ),
        f"responses: {len(have)} judged, {len(results) - len(have)} with no numbers",
        "",
        " id  kind         detection  quality",
    ]
    for r in results:
        n = r["numbers"]
        numbers = "    -        -" if n is None else f"{n['detection']:.2f}       {n['quality']:.2f}"
        lines.append(f"{r['id']:>3}  {r['kind']:11}  {numbers}")
    return "\n".join(lines) + "\n"


def main(only: set[int] | None) -> None:
    rows = read_responses(only)
    if not rows:
        sys.exit("no responses matched")
    RUNS.mkdir(exist_ok=True)
    if hasattr(harness, "TRACE_PATH"):
        harness.TRACE_PATH = RUNS / "trace.jsonl"  # your own trace.jsonl is left alone
    else:
        os.chdir(RUNS)
    print(f"{len(rows)} saved response(s). The decider reads each one: a second or two each on a Mac,")
    print("longer on a computer without a graphics card.\n")
    results = []
    for row in rows:
        numbers, said = judged(row)
        results.append({**row, "numbers": numbers, "said": said})
        print(row_text(results[-1]), flush=True)
    if all(r["numbers"] is None for r in results):
        sys.exit("\nNo response got its numbers. Is the decider server running?")
    TABLE_PATH.write_text(table(results), encoding="utf-8")
    print(f"\n{TABLE_PATH.read_text(encoding='utf-8')}\nsaved to bench/sweep.txt")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show what each threshold sends, over bench/responses.jsonl.")
    parser.add_argument("--only", help="response ids, comma-separated: 1,11,21")
    args = parser.parse_args()
    main({int(n) for n in re.findall(r"\d+", args.only)} if args.only else None)
