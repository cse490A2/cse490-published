"""Check that your router asks a second question when settings.json lists one.

run, from your harness folder (the decider server must be running):
    source .venv-harness/bin/activate
    python bench/check_router.py

The handout's step 1 adds a question named detection to router.questions in
settings.json. This check tries that for one run: it copies settings.json
aside, adds the question, asks the harness one short prompt, and puts
settings.json back. It passes when
the newest router_judge record in trace.jsonl holds a number under detection and a
number under quality, which means one decider call carried both questions.

It works on any harness that follows ROUTER.md. It changes no file but
trace.jsonl, which gains the records of the one prompt.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

DETECTION = {"question": "Does the response contain program code?"}
PROMPT = "Reply with the one word: ready."
FOR_THE_AGENT = (
    "Read ROUTER.md again: the decider call must carry every question under router.questions "
    "in settings.json, so with a question named detection there, the router_judge record must hold detection."
)


def load_settings(folder: Path) -> tuple[dict | None, str]:
    """Return settings.json and "", or None and what is wrong with its router section."""
    try:
        settings = json.loads((folder / "settings.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, "settings.json is missing or is not valid JSON."
    section = settings.get("router")
    if not isinstance(section, dict) or not section.get("decider_url"):
        return None, "settings.json has no router section with a decider_url."
    if not section.get("enabled"):
        return None, 'The router section in settings.json says "enabled": false.'
    return settings, ""


def decider_answers(url: str) -> bool:
    """Return True when the decider server answers one small request."""
    body = {"state": "hello", "questions": {"q": {"type": "noul", "instructions": "Is this a greeting?"}}}
    request = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as reply:
            return "answers" in json.loads(reply.read())
    except (OSError, ValueError):
        return False


def trace_lines(folder: Path) -> list[str]:
    """Return the lines of trace.jsonl, or none when the file is not there."""
    try:
        return (folder / "trace.jsonl").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def newest_judgment(lines: list[str]) -> dict | None:
    """Return the last router_judge record among the lines, or None."""
    for line in reversed(lines):
        if '"router_judge"' not in line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get("type") == "router_judge" or record.get("event") == "router_judge":
            return record
    return None


def ask_with_detection(folder: Path, settings: dict) -> tuple[dict | None, str]:
    """Run the harness once with a question named detection. Return its new judgment and its output."""
    path = folder / "settings.json"
    aside = folder / "settings.json.before-check"
    before = len(trace_lines(folder))
    shutil.copy2(path, aside)
    try:
        questions = settings["router"].get("questions")
        if not isinstance(questions, dict):
            questions = settings["router"]["questions"] = {}
        questions.setdefault("detection", dict(DETECTION))
        path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        try:
            ran = subprocess.run(
                [sys.executable, "harness.py"],
                input=PROMPT + "\n",
                capture_output=True,
                text=True,
                timeout=300,
                cwd=folder,
            )
            said = (ran.stdout or "") + "\n" + (ran.stderr or "")
        except subprocess.TimeoutExpired:
            said = "The harness did not finish in five minutes."
    finally:
        shutil.copy2(aside, path)  # settings.json is back as it was, whatever happened
        aside.unlink()
    return newest_judgment(trace_lines(folder)[before:]), said


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def main() -> int:
    folder = Path.cwd()
    if not (folder / "harness.py").is_file():
        print("There is no harness.py here. Run this from your harness folder.")
        return 1
    settings, wrong = load_settings(folder)
    if settings is None:
        print(f"Not passed. {wrong} Add the router section from ROUTER.md, then run this again.")
        return 1
    url = settings["router"]["decider_url"]
    if not decider_answers(url):
        print(f"Not run. The decider server does not answer at {url}. Start it, then run this again.")
        return 1

    print("Asking the harness one prompt with a question named detection added to router.questions ...")
    record, said = ask_with_detection(folder, settings)
    last = next((line.strip() for line in reversed(said.splitlines()) if line.strip()), "it printed nothing")
    if record is None:
        print("Not passed. The harness wrote no router_judge record to trace.jsonl for that prompt.")
        print(f"Its last line: {last[:200]}")
        print("If it could not reach the course gateway: off campus, connect the UW VPN, then run this again.")
        print("If it has no router yet, ask your coding agent: Read ROUTER.md and follow it.")
        return 1
    if record.get("status") == "failure":
        print("Not passed. The router could not reach the decider for that prompt:")
        print(f"  {record.get('error_message', last)}")
        return 1
    detection, quality = record.get("detection"), record.get("quality")
    if is_number(detection) and is_number(quality):
        print(f"Passed. One decider call answered both questions: detection {detection:.2f}, quality {quality:.2f}.")
        print("settings.json is back as it was. You are ready for the handout's step 1.")
        return 0
    print("Not passed. The router_judge record holds "
          + ("quality but no detection." if is_number(quality) else "no number under quality."))
    print("Give your coding agent this sentence, then run this check again:")
    print(f"  {FOR_THE_AGENT}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
