# ROUTER: hook the strands decider into harness.py

Give this file to your coding agent from inside your `harness` folder. It
describes one section in `settings.json` and one change to `harness.py`. The
names below are the ones the course harness uses; if yours differ, use yours.

## What the router does

The default model answers each prompt the way it always has. Before the reply
is printed, the harness sends the question, the tool calls the model made with
their results, and the reply to the strands decider running on this computer,
as one yes/no question named `quality`. The decider returns the probability that
the answer is good. Below `router.threshold`, the harness drops the reply and answers the same
question again, tools and all, with `router.fallback_model`.

## settings.json

1. Set the default model to the smaller model the router checks:
   `"model": {"default": "internal/Qwen3.6-35B-A3B", ...}`. The fallback must be
   a different, stronger model, or the router asks the same model twice.
2. Add this section beside `model`:

```json
"router": {
  "enabled": true,
  "decider_url": "http://127.0.0.1:8000/v1/systemone",
  "fallback_model": "external/haiku-5-5",
  "threshold": 0.5,
  "question": "Does the response correctly and completely answer the user's question?",
  "timeout_seconds": 60,
  "max_state_chars": 12000
}
```

Read every key through the harness's `setting(section, key, default)` helper,
with the values above as the defaults, except `enabled`, whose default is
`false`: a harness with no `router` section runs as it did before.

## harness.py

1. **Pick the model per request.** `chat_request(context, tools, model=None)` and
   `call_model(context, tools, model=None)` take an optional `model`. When it is
   set, it is sent in place of the agent's model for that one request.
   `answer(...)` takes the same `model=None` and passes it to `call_model`.
2. **Add `judge(question, response, steps) -> float | None`.**
   - `question` is the user's prompt this turn, `context[turn_start]["content"]`.
     `steps` is `context[turn_start + 1 : -1]`: assistant messages carrying
     `tool_calls`, and the `role: "tool"` messages with their results. Pair each
     call with its result by `tool_call_id`.
   - Write the tool steps as numbered lines,
     `1. read_file({"path":"settings.json"}) -> <result>`, using the raw
     `function.arguments` string. A result that is not a string goes through
     `json.dumps` first; then collapse whitespace to single spaces; then cut
     the result at 600 characters and add ` [cut]`. With no tool calls, write
     `(no tools used)`.
   - Build the state from three parts. Cut each body, then put its header
     above it: `User question:\n` + question cut to `max_state_chars // 6`;
     `Tools the model used, with their results:\n` + the lines cut to `// 2`;
     `Model response:\n` + response cut to `// 3`. Join the three with a
     blank line.
   - POST it with `urllib.request` to `router.decider_url`, with
     `router.timeout_seconds` as the timeout. Do not reuse the gateway's
     `send()`: its errors and hints are about the gateway.
     `{"state": <state>, "questions": {"quality": {"type": "noul", "instructions": <router.question>}}}`
   - The answer is the number at `answers.quality.noul`, between 0 and 1.
   - Catch every way the call can fail: `OSError` (which covers a refused
     connection, an HTTP error status and a timeout), `ValueError` (a reply
     that is not JSON), and `KeyError` or `TypeError` (no number at
     `answers.quality.noul`). For any of them, print
     `[router] decider unreachable (<error>); keeping the reply.` and return
     `None`. One failed judgment never stops the turn.
   - Append one `router_judge` record to `trace.jsonl` with `append_trace`:
     on success `status="success"`, `question`, `tools_used` (the numbered
     lines), `response`, `quality` and `duration_ms`; on failure
     `status="failure"` and `error_message`.
3. **Hook it into `answer()`.** In the branch where the reply has no
   `tool_calls`, after the reply is appended to the context and before
   `say(...)` prints it, and only when `model is None` (so the fallback's own
   reply is never judged), `router.enabled` is true and a `fallback_model` is set:
   - run `judge` through `in_background(...)`, since it blocks;
   - if the result is `None`, keep the reply and print nothing more: `judge`
     already said why;
   - if the result is below `router.threshold`, print
     `[router] judged 0.31 < 0.5: asking external/haiku-5-5 instead.`
     (two decimals for the probability), delete `context[turn_start + 1 :]` so
     only the question is left, and return
     `await answer(context, tools, sessions, deny, model=fallback)`;
   - otherwise print `[router] judged 0.82: keeping the reply.` and go on to `say`.

A turn makes at most one extra model call. A gateway error leaves the turn as
the harness already handles it; the router does not step in.

## Done when

With the decider server running, from `harness`:
`printf 'Read settings.json and tell me which model is the default.\n' | .venv-harness/bin/python harness.py`
prints a `[router] judged` line before the reply, and `trace.jsonl` holds a
`router_judge` record.
