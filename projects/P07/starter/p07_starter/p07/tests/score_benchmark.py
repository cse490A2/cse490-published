"""Score an answers file from the multi-agent benchmark.

    python tests/score_benchmark.py answers.jsonl

Prints one row per question and the total. The key beside this file,
benchmark_key.json, holds a fingerprint of each answer and never the answer
itself, so the score can be checked without the answers being readable.

An answer is right when it matches after case, spaces, commas and dollar
signs are dropped. The last question is the summary. It is right when the
team's own answers to the questions it rests on are right, and the summary
states each of them.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
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
    given = read_answers(Path(sys.argv[1]))
    right: dict[str, bool] = {}
    for number, key in KEY["answers"].items():
        answer = given.get(number, {}).get("answer", "(none)")
        right[number] = fingerprint(number, answer) == key
        print(f"{number:>2}  {'right' if right[number] else 'WRONG':<5}  {str(answer)[:40]}")

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


if __name__ == "__main__":
    main()
