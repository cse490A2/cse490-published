# TRACE.md: wiring trace.py into your own harness

The agent view draws what your agents do from one file, trace.jsonl. trace.py writes that
file. This spec says where your harness.py calls it. The starter harness is wired already.

Give this file to an agent, with harness.py and trace.py, and ask it to wire the trace in.

## What you start with

trace.py sits beside harness.py. It gives two functions:

| Function | What it writes |
|---|---|
| `append_trace(kind, **fields)` | One line of the kind you name, with the fields you pass. |
| `trace_model_call(context, started, body, headers)` | One `model_call` line for a call the model answered. |
| `trace_model_call(context, started, error=error)` | One `model_call` line for a call that failed. |

Every line is stamped with the time, the session and the agent. You pass none of those.

## The import

Near the top of harness.py, after the other imports:

    from trace import append_trace, trace_model_call

## The five calls

| When | The call |
|---|---|
| At startup, once for each MCP server, after it lists its tools | `append_trace("server_tools", server=name, tools=[...])` |
| Just before a tool runs, local or server | `append_trace("tool_call", name=name, arguments=args)` |
| When the tool has returned | `append_trace("tool_reply", name=name, reply=result)` |
| When the model has answered | `trace_model_call(context, started, body, headers)` |
| When the model call failed | `trace_model_call(context, started, error=error)` |

- `tools` is the list of the server's tool names.
- `arguments` is the dictionary the model sent. `reply` is the text the tool returned.
- `context` is the list of messages that was sent to the model.
- `started` is `time.time()`, taken on the line before the request is sent.
- `body` is the gateway's whole reply as a dictionary. `headers` is its response headers
  as a dictionary. The tokens and the cost are read from these two.

A harness that keeps only the model's message, and not the whole reply, writes a shorter
line. The opening comment of trace.py shows it.

## Rules

- Add calls. Change nothing else that harness.py does.
- A tool call and its reply are traced as a pair, in that order, for every tool.
- Trace a failed model call too. The agent view shows it as a failure.
- A long reply is traced whole. Shorten what is printed on screen, never what is traced.
- Nothing from .env goes into a trace line: no key, no token.

## Check it

1. Start the harness and give it one prompt that uses a tool, such as: read settings.json
   and tell me the model.
2. Leave with Ctrl+D, then count the lines of each kind:

       python3 -c "import json,collections; print(collections.Counter(json.loads(l)['type'] for l in open('trace.jsonl')))"

It is wired when the count shows `model_call`, `tool_call` and `tool_reply`, with as many
`tool_reply` lines as `tool_call` lines. `server_tools` is there when settings.json names an
MCP server. Then open the agent view: the prompt, the tool and its reply are on one row.
