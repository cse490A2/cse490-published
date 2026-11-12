"""Test for cost: calls, tokens and cost per agent and per model, from trace.jsonl."""

import json
from pathlib import Path

from toolcheck import check, numbers, tool

cost = tool("cost", [])

none_yet = cost()
check(
    none_yet.startswith("Error: no trace.jsonl yet"),
    "Without a trace, cost returns: Error: no trace.jsonl yet",
    none_yet,
)


def call(
    agent: str, model: str, prompt: int, completion: int, spend: float | None
) -> dict:
    """Return one model_call line in the shape trace.py writes."""
    return {
        "type": "model_call",
        "agent": agent,
        "status": "success",
        "model": {"model_group": model},
        "tokens": {
            "prompt": prompt,
            "completion": completion,
            "total": prompt + completion,
        },
        "spend": spend,
    }


TRACE = [
    {"type": "server_tools", "agent": "main", "tools": ["list_issues"]},
    call("main", "model-a", 1000, 200, 0.25),
    {"type": "tool_call", "agent": "main", "name": "read_file"},
    call("main", "model-b", 300, 40, 0.5),
    call("helper-1", "model-a", 2000, 500, None),  # tokens, no cost: still counts
    call("helper-1", "model-b", 70, 7, 0.125),
    {  # a call that failed has no tokens and no cost
        "type": "model_call",
        "agent": "helper-1",
        "status": "failure",
        "model": {"model_group": None},
        "tokens": {"prompt": None, "completion": None, "total": None},
        "spend": None,
    },
]
Path("trace.jsonl").write_text(
    "".join(json.dumps(line) + "\n" for line in TRACE), encoding="utf-8"
)

table = cost()
check(not table.startswith("Error"), "With a trace, cost returns a table.", table)

# Per row: the total tokens (or prompt and completion apart), and the cost.
ROWS = {
    "main": (1540, 1300, 240, 0.75),
    "helper-1": (2577, 2070, 507, 0.125),
    "model-a": (3700, 3000, 700, 0.25),
    "model-b": (417, 370, 47, 0.625),
}
for label, (total, prompt, completion, spend) in ROWS.items():
    rows = [
        numbers(line.replace(label, "")) for line in table.splitlines() if label in line
    ]
    check(rows, f"The table has a row for {label}.", table)
    check(
        any(total in row or (prompt in row and completion in row) for row in rows),
        f"The row for {label} sums its tokens: {total} in total "
        f"({prompt} in, {completion} out). A call with no cost still counts.",
        table,
    )
    check(
        any(any(abs(value - spend) < 0.006 for value in row) for row in rows),
        f"The row for {label} sums its cost: {spend}.",
        table,
    )
print("ok")
