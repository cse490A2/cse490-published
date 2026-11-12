"""The trace: one line in trace.jsonl for each thing an agent does.

Put this file beside your harness and import what you need:

    from trace import append_trace, trace_model_call

Every line is one JSON object, stamped with its type, the time, the session
and the agent. The agent view (agent_view/) reads this file while it grows.

The lines a harness writes, and when:

    at startup, once per MCP server
        append_trace("server_tools", server="github", tools=[...])
    just before a tool runs
        append_trace("tool_call", name=name, arguments=args)
    when the tool has returned
        append_trace("tool_reply", name=name, reply=result)
    when the model has answered
        trace_model_call(context, started, body, headers)
    when the model call failed
        trace_model_call(context, started, error=error)

trace_model_call wants the gateway's whole reply (body) and its response
headers, so it can record tokens, cost and the call's id. A harness that
keeps only the message can write a shorter line of its own:

    names = [c["function"]["name"] for c in message.get("tool_calls") or []]
    append_trace("model_call", status="success",
                 turn={"origin": "user", "user_prompt": prompt},
                 response_text=message.get("content"), tool_names=names)

Standard library only. Nothing here calls the model or changes a file other
than trace.jsonl.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any

TRACE_PATH = Path("trace.jsonl")  # in the folder the harness is run from
CLIENT_NAME = "cse490-harness"

# One id per start of the harness, so the lines of one sitting can be found
# together. A harness that starts copies of itself hands them this id.
SESSION_ID = os.environ.get("HARNESS_SESSION") or str(uuid.uuid4())

# Who is writing. A harness with one agent leaves this alone; one that runs
# several sets it at startup: trace.AGENT = "helper-1".
AGENT = "main"


def append_trace(kind: str, **fields: Any) -> None:
    """Append one event to trace.jsonl, stamped with when and by whom."""
    line = {
        "type": kind,
        "time": utc(time.time()),
        "session": SESSION_ID,
        "agent": AGENT,
        **fields,
    }
    with TRACE_PATH.open("a", encoding="utf-8") as trace:
        trace.write(json.dumps(line) + "\n")


def utc(seconds: float) -> str:
    """Return a clock time as the gateway's logs write it: UTC, to the millisecond."""
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(seconds))
    return f"{stamp}.{int(seconds % 1 * 1000):03d}Z"


def number(text: str | None) -> float | None:
    """Return a header's value as a number, or None when it is absent."""
    try:
        return float(text) if text is not None else None
    except ValueError:
        return None


def model_call_record(
    context: list[dict], started: float, ended: float, body: dict, headers: dict
) -> dict:
    """Describe one model call in the field names of the gateway's own logs.

    The gateway keeps a record of every call under these names. Writing the
    same names here lets a line of trace.jsonl be matched to the gateway's
    record of the same call by session.litellm_call_id or request_id.
    """
    usage = body.get("usage") or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}
    choice = (body.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    tool_calls = message.get("tool_calls") or []
    asked_by_user = bool(context) and context[-1].get("role") == "user"
    return {
        "request_id": body.get("id"),
        "finish_reason": choice.get("finish_reason"),
        "response_text": message.get("content"),
        "tool_names": [call["function"]["name"] for call in tool_calls] or None,
        "turn": {
            "origin": "user" if asked_by_user else "automated",
            "user_prompt": context[-1].get("content") if asked_by_user else None,
        },
        "model": {
            "model_group": headers.get("x-litellm-model-group") or body.get("model"),
            "model": headers.get("x-litellm-model-name"),
            "model_id": headers.get("x-litellm-model-id"),
        },
        "tokens": {
            "prompt": usage.get("prompt_tokens"),
            "completion": usage.get("completion_tokens"),
            "total": usage.get("total_tokens"),
            "reasoning": completion_details.get("reasoning_tokens"),
            "cache_read": prompt_details.get("cached_tokens"),
            "cache_creation": prompt_details.get("cache_creation_tokens"),
        },
        "spend": number(headers.get("x-litellm-response-cost")),
        "key": {
            "spend": number(headers.get("x-litellm-key-spend")),
            "max_budget": number(headers.get("x-litellm-key-max-budget")),
        },
        "timestamps": {
            "start_time": utc(started),
            "end_time": utc(ended),
            "request_duration_ms": round((ended - started) * 1000),
            "gateway_duration_ms": number(
                headers.get("x-litellm-response-duration-ms")
            ),
        },
        "session": {
            "session_id": SESSION_ID,
            "litellm_call_id": headers.get("x-litellm-call-id"),
        },
        "client": {"name": CLIENT_NAME, "messages_sent": len(context)},
    }


def trace_model_call(
    context: list[dict],
    started: float,
    body: dict | None = None,
    headers: dict | None = None,
    error: Exception | None = None,
) -> None:
    """Record one model call, answered or failed, in trace.jsonl.

    context is the list of messages that was sent. started is time.time()
    taken just before the request. Pass body and headers when the model
    answered, or error when the call failed.
    """
    append_trace(
        "model_call",
        status="failure" if error else "success",
        error_code=getattr(error, "code", None),
        error_message=str(error) if error else None,
        **model_call_record(context, started, time.time(), body or {}, headers or {}),
    )
