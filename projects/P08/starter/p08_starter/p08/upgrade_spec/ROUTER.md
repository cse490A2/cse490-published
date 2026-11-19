# ROUTER: hook the strands decider into harness.py

Give this file to your coding agent from inside your `harness` folder. It
describes one section in `settings.json` and one change to `harness.py`. The
names below are the ones the course harness uses; if yours differ, use yours.

## What the router does

The default model answers each prompt the way it always has. Before the reply
is printed, the harness sends the question, the tool calls the model made with
their results, and the reply to the strands decider running on this computer,
with the questions `settings.json` lists under `router.questions`. Setup lists
one, a yes/no question named `quality`. The decider returns the probability that
the answer is good. Below `router.threshold`, the harness drops the reply and answers the same
question again, tools and all, with `router.fallback_model`.

The router can ask a second question in the same call. `router.questions` is an
object with one entry for each question: a name, and the question in plain
words, `"<name>": {"question": "<the question>"}`. The harness asks the decider
every entry. When there is also a question named `detection`, the rule has two parts:
the reply goes to the fallback model only when `detection` is at least 0.5 and
`quality` is below `router.threshold`. With `quality` alone, the rule is
`quality` alone. There is one decider call for every response, never two.
Setup ends with `quality` alone; the Project 8 handout adds `detection` by editing
`settings.json`, so the harness must already handle both cases.

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
  "questions": {
    "quality": {"question": "Does the response correctly and completely answer the user's question?"}
  },
  "timeout_seconds": 60,
  "max_state_chars": 12000
}
```

Read every key through the harness's `setting(section, key, default)` helper,
with the values above as the defaults, except `enabled`, whose default is
`false`: a harness with no `router` section runs as it did before.

`questions` holds only `quality` here: do not add a `detection` entry to
`settings.json`. The harness must still handle one when it is there.

## harness.py

1. **Pick the model per request.** `chat_request(context, tools, model=None)` and
   `call_model(context, tools, model=None)` take an optional `model`. When it is
   set, it is sent in place of the agent's model for that one request.
   `answer(...)` takes the same `model=None` and passes it to `call_model`.
2. **Add `judge(question, response, steps) -> dict | None`.**
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
     `Model response:\n` + the response. Join the three with a blank line.
   - The response keeps its end, where the code usually is, and may use the
     room the tool lines left: its room is `max_state_chars // 3` plus
     whatever of the tool lines' `// 2` they did not use. A response longer
     than its room is sent as `[cut] ` + its last `room` characters.
   - The decider reads at most 4096 tokens and answers HTTP 422 to more. On
     a 422 (`urllib.error.HTTPError` with `code == 422`), send the request
     once more with half the response's room. Any other error, and a second
     422, is a failed judgment as below.
   - POST it with `urllib.request` to `router.decider_url`, with
     `router.timeout_seconds` as the timeout. Do not reuse the gateway's
     `send()`: its errors and hints are about the gateway.
     `{"state": <state>, "questions": {<name>: {"type": "noul", "instructions": <its question>}, ...}}`
     with one entry for each entry in `router.questions`, under the same
     name. Do not write any question's name or wording in the program: loop over the
     setting. A name other than `quality` and `detection` is asked and recorded
     like the others and does not change the rule.
   - When `router.questions` is not an object or has no entry named
     `quality`, send nothing: print
     `[router] settings.json has no question named quality; keeping the reply.`,
     record a failed judgment and return `None`.
   - The answers are the numbers at `answers.<name>.noul`, one for each name
     in `router.questions`, each between 0 and 1. Return them as a dict by
     name, such as `{"quality": 0.87}` or `{"quality": 0.31, "detection": 0.92}`.
   - Catch every way the call can fail: `OSError` (which covers a refused
     connection, an HTTP error status and a timeout), `ValueError` (a reply
     that is not JSON), and `KeyError` or `TypeError` (a number
     missing from the answers). For any of them, print
     `[router] decider unreachable (<error>); keeping the reply.` and return
     `None`. One failed judgment never stops the turn.
   - Append one `router_judge` record to `trace.jsonl` with `append_trace`:
     on success `status="success"`, `question`, `tools_used` (the numbered
     lines), `response`, `duration_ms`, and one field for each question's
     name holding its number: `quality`, and `detection` when `router.questions`
     has it (no `detection` field otherwise); on failure
     `status="failure"` and `error_message`.
3. **Hook it into `answer()`.** In the branch where the reply has no
   `tool_calls`, after the reply is appended to the context and before
   `say(...)` prints it, and only when `model is None` (so the fallback's own
   reply is never judged), `router.enabled` is true and a `fallback_model` is set:
   - run `judge` through `in_background(...)`, since it blocks;
   - if the result is `None`, keep the reply and print nothing more: `judge`
     already said why;
   - with no `detection` number, the reply is sent on when `quality` is below
     `router.threshold`. With a `detection` number, it is sent on only when `detection`
     is at least 0.5 and `quality` is below `router.threshold`;
   - when the reply is sent on, print
     `[router] judged 0.31 < 0.5: asking external/haiku-5-5 instead.`
     or, with a `detection` number,
     `[router] judged detection 0.91, quality 0.31 < 0.5: asking external/haiku-5-5 instead.`
     (two decimals for each probability), delete `context[turn_start + 1 :]`
     so only the question is left, and return
     `await answer(context, tools, sessions, deny, model=fallback)`;
   - otherwise print `[router] judged 0.82: keeping the reply.` or, with a
     `detection` number, `[router] judged detection 0.12, quality 0.31: keeping the reply.`
     and go on to `say`.

A turn makes at most one extra model call. A gateway error leaves the turn as
the harness already handles it; the router does not step in.

## Done when

With the decider server running, from `harness`:
`printf 'Read settings.json and tell me which model is the default.\n' | .venv-harness/bin/python harness.py`
prints a `[router] judged` line before the reply, and `trace.jsonl` holds a
`router_judge` record with `quality` and no `detection`.

Then `.venv-harness/bin/python bench/check_router.py` passes. It adds a question
named `detection` to `router.questions` for one run, asks the harness one prompt, puts
`settings.json` back, and looks for a `router_judge` record that holds numbers
under both `detection` and `quality`.
