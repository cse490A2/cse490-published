"""
Measure where to set router.threshold.

run, from your harness folder (the decider server must be running):
    source .venv-harness/bin/activate
    python bench/sweep.py
    python bench/sweep.py --only 1,7,13    just these prompts

Every prompt in bench/prompts.jsonl is answered by the default model, and the
decider is asked your router's two questions about the reply: code (is this a
programming task) and quality (is the reply a good answer). The fallback model
is never called. Each prompt carries a label: "keep" when the reply should stay
with the default model, "send" when it should go to the fallback model.

A reply goes to the fallback model when code is at least 0.5 and quality is
below the threshold. For each threshold from 0.1 to 0.9 the table counts the
prompts that land on the side their label says, and how many would go to the
fallback model. The
table is saved to bench/sweep.txt.

Each prompt runs in its own folder under bench/runs/, holding copies of
settings.json and systemprompt.md, so your harness folder and your own
trace.jsonl are left alone.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import io
import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent  # harness/bench
HARNESS = HERE.parent  # harness: harness.py, settings.json, .env
sys.path.insert(0, str(HARNESS))
import harness  # noqa: E402

PROMPTS_PATH = HERE / "prompts.jsonl"
TABLE_PATH = HERE / "sweep.txt"
COPIED_FILES = [HARNESS / "settings.json", HARNESS / "systemprompt.md"]
THRESHOLDS = [round(0.1 * step, 1) for step in range(1, 10)]
CODE_CUT = 0.5  # code at or above this: the reply is a programming task
HEADER = " id  label  code  quality"


def read_prompts(only: set[int] | None) -> list[dict]:
    """Return the rows of prompts.jsonl, or just the chosen ids."""
    lines = PROMPTS_PATH.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    for row in rows:
        if row.get("label") not in {"keep", "send"}:
            sys.exit(f"prompt {row.get('id')}: label must be keep or send")
    return [row for row in rows if not only or row["id"] in only]


def last_judgment(folder: Path) -> dict | None:
    """Return the code and quality numbers of the folder's last router_judge record."""
    trace = folder / "trace.jsonl"
    if not trace.exists():
        return None
    for line in reversed(trace.read_text(encoding="utf-8").splitlines()):
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get("event") == "router_judge" or record.get("type") == "router_judge":
            if record.get("status") == "failure":
                return None
            if "quality" in record and "code" not in record:
                sys.exit(
                    "\nYour router_judge record has quality but no code: the router "
                    "still asks one question. Do the handout's step 2 first."
                )
            if "code" in record and "quality" in record:
                return {"code": float(record["code"]), "quality": float(record["quality"])}
            return None
    return None


async def run_one(row: dict, folder: Path) -> dict | None:
    """Answer one prompt with the default model, then return the decider's two numbers."""
    folder.mkdir(parents=True)
    for source in COPIED_FILES:
        shutil.copy2(source, folder / source.name)
    os.chdir(folder)  # the harness's file tools and trace.jsonl work in the cwd

    system = harness.PROMPT_PATH.read_text(encoding="utf-8") + harness.skills_index()
    context = [
        {"role": "system", "content": system},
        {"role": "user", "content": row["prompt"]},
    ]
    shown = io.StringIO()
    with contextlib.redirect_stdout(shown):  # keep the harness's prints out of the table
        await harness.answer(context, harness.LOCAL_DEFINITIONS, {}, set())
    if len(context) < 3 or context[-1].get("role") != "assistant":
        print(f"  no reply: {' '.join(shown.getvalue().split())[:120]}")
        return None
    reply = context[-1].get("content") or ""
    with contextlib.redirect_stdout(shown):
        harness.judge(row["prompt"], reply, context[2:-1])
    return last_judgment(folder)  # read from the trace, as the grader does


def sent(numbers: dict, threshold: float) -> bool:
    """Return True when the router would send this reply to the fallback model."""
    return numbers["code"] >= CODE_CUT and numbers["quality"] < threshold


def row_text(result: dict) -> str:
    """Return one line of the per-prompt table."""
    numbers = result["numbers"]
    if numbers is None:
        return f"{result['id']:>3}  {result['label']:5}     -        -"
    return f"{result['id']:>3}  {result['label']:5}  {numbers['code']:.2f}     {numbers['quality']:.2f}"


def table(results: list[dict]) -> str:
    """Return the per-prompt numbers and the count at each threshold."""
    judged = [r for r in results if r["numbers"] is not None]
    lines = [
        f"code question: {harness.setting('router', 'code_question', '')}",
        f"quality question: {harness.setting('router', 'question', '')}",
        f"rule: send when code >= {CODE_CUT} and quality < threshold",
        f"model: {harness.setting('model', 'default', harness.DEFAULT_MODEL)}",
        f"prompts: {len(judged)} judged, {len(results) - len(judged)} with no numbers",
        "",
        HEADER,
    ]
    lines += [row_text(r) for r in results]
    lines += ["", "threshold  right side  sent to fallback"]
    for threshold in THRESHOLDS:
        gone = [r for r in judged if sent(r["numbers"], threshold)]
        right = sum(sent(r["numbers"], threshold) == (r["label"] == "send") for r in judged)
        lines.append(f"{threshold:9.1f}  {right:>10}  {len(gone):>16}")
    return "\n".join(lines) + "\n"


async def main(only: set[int] | None) -> None:
    rows = read_prompts(only)
    if not rows:
        sys.exit("no prompts matched")
    harness.SETTINGS.setdefault("router", {})["enabled"] = False  # no fallback call
    run_folder = HERE / "runs" / time.strftime("%Y%m%d-%H%M%S")
    print(f"{len(rows)} prompt(s), about 20 seconds each\n\n{HEADER}")
    results = []
    for row in rows:
        numbers = await run_one(row, run_folder / f"p{row['id']:02d}")
        os.chdir(HARNESS)
        results.append({**row, "numbers": numbers})
        print(row_text(results[-1]))
    if all(r["numbers"] is None for r in results):
        sys.exit("\nNo prompt got its numbers. Is the decider server running?")
    TABLE_PATH.write_text(table(results), encoding="utf-8")
    print(f"\n{TABLE_PATH.read_text(encoding='utf-8')}\nsaved to bench/sweep.txt")


if __name__ == "__main__":
    load_dotenv(HARNESS / ".env")
    parser = argparse.ArgumentParser(description="Sweep the router threshold over bench/prompts.jsonl.")
    parser.add_argument("--only", help="prompt ids, comma-separated: 1,7,13")
    args = parser.parse_args()
    asyncio.run(main({int(n) for n in re.findall(r"\d+", args.only)} if args.only else None))
