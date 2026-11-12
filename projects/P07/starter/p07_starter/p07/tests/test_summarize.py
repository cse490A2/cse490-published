"""Test for summarize: five lines from the model, asked through call_model.

This test makes one real call to the model. It needs the key in .env and,
off campus, the UW VPN.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from toolcheck import HOME, check, harness, is_error, tool

load_dotenv(HOME / ".env")
check(
    os.environ.get("LITELLM_API_KEY") and os.environ.get("LITELLM_BASE_URL"),
    "summarize calls the model, so .env beside harness.py needs "
    "LITELLM_API_KEY and LITELLM_BASE_URL.",
)

Path("harbor.txt").write_text(
    "The harbor at Alder Point opened in 1887 to ship timber south.\n"
    "A lighthouse was added in 1902 after two schooners ran aground.\n"
    "Its lamp turned twice a minute and burned whale oil, then kerosene.\n"
    "The timber trade ended in the 1930s and the docks fell quiet.\n"
    "Fishing boats took the empty berths during the 1950s.\n"
    "A storm in 1962 broke the north pier, and it was never rebuilt.\n"
    "The lighthouse was automated in 1978 and its keeper retired.\n"
    "Today the harbor holds forty boats and a small museum.\n"
    "The museum keeps the old lamp and the keeper's log books.\n"
    "Each August the town rows a race from the pier to the light.\n",
    encoding="utf-8",
)

# Count the calls that reach the harness's own call_model, and keep what was sent.
sent = []
real_call_model = harness.call_model


def counted(context: list[dict], tools: list[dict]) -> dict:
    """Record the call, then make it."""
    sent.append((context, tools))
    return real_call_model(context, tools)


harness.call_model = counted

summarize = tool("summarize", ["path"])
summary = summarize(path="harbor.txt")

check(len(sent) == 1, "summarize asks the model once, through call_model.", len(sent))
check(not is_error(summary), "The model's answer comes back.", summary)
context, tools = sent[0]
check(len(context) == 1, "It sends one message.", len(context))
check(not tools, "It sends no tools.", tools)
check("lighthouse" in str(context).lower(), "The message holds the file's content.")
lines = [line for line in summary.splitlines() if line.strip()]
check(len(lines) == 5, "The summary is five lines.", summary)

outside = summarize(path=".env")
check(
    is_error(outside) and len(sent) == 1,
    "A key file is refused, and never sent.",
    outside,
)
print("ok")
