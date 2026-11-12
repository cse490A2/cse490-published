# SPAWN.md: the /spawn command to add to this harness

`/spawn <goal>` hands one goal to a team. The harness starts a manager. The manager splits
the goal into tasks and starts one helper per task, all at once. It reads their reports,
then answers with its own report.

    /spawn <goal>     typed in the chat
         |
      manager         a copy of harness.py: splits the goal into tasks
         |
      helpers         copies of harness.py, one task each, all at once
         |
      manager         reads their reports: done, or another round
         |
      report          printed in the chat and added to the conversation

## A command, not a tool

`/spawn` is typed by the person at the keyboard. The model cannot start it. It goes in the
`COMMANDS` list beside `/plan`, `/approve` and `/cancel`, as one function named `spawn`.

- With no goal it prints how to use it and starts nothing.
- While plan mode is on it refuses, and says to approve or cancel the plan first.
- When the run ends, the goal and the manager's report are added to the conversation, so
  the next prompt can ask about them.

## An agent is a copy of the program

A manager or a helper is harness.py started again, as a separate process, with three
arguments:

    python harness.py --role manager --name manager --task "<the goal>"
    python harness.py --role helper --name helper-1 --task "<one task>"

A copy started with `--task` reads no prompt. It runs its one task through the same loop
the chat uses, prints the line `=== report ===`, prints its last reply, and ends. Whoever
started it reads the text after that line as the report. A copy that ends with no such
line reports the end of its output and its exit code.

A copy starts with no memory of the chat. It knows its role's prompt and its task.

## The two roles

| | Manager | Helper |
|---|---|---|
| Prompt | Split the goal, start the helpers in one call, read the reports, check the work, report. | Do the one task and nothing more, touch only the files it names, report. |
| Gains | The `start_helpers` tool. | Nothing. |
| Is refused | `write_file`. A manager never writes a file: a helper does. | Nothing. |
| Model | `manager_model` in settings.json, or the default model. | `helper_model` in settings.json, or the default model. |

Only the manager has `start_helpers`. The chat does not have it, and a helper does not have
it, so a helper cannot start helpers of its own.

## The start_helpers tool

    start_helpers(tasks)

`tasks` is a list of text, one task per helper. This is the one tool whose argument is not
a single string, so the tool's definition has to describe `tasks` as a list of strings.

- It starts every helper before it waits for any of them.
- Helpers are named helper-1, helper-2 and so on, counting up across every call.
- It returns every report in one text, each under a heading with the helper's name.
- A task says what to do, which files the helper owns, and what done means. The helper
  knows nothing else.

## The two limits

| Setting | What it limits | When it is passed |
|---|---|---|
| `max_helpers` | The helpers one call may start. | The call starts nothing and returns `refused: 9 helpers in one call is over max_helpers 8 under spawn in settings.json`. |
| `max_minutes` | The whole run, helpers included, from the moment `/spawn` is typed. | Every copy still running is stopped. The report starts with `[stopped at the time limit: ...]`. |

The time limit is one clock for the whole team. `/spawn` works out the moment the run must
end and hands it to the manager, and the manager hands the same moment to each helper. A
helper started in the last minute gets one minute, not a fresh five.

Ctrl+C during a run stops the manager and every helper. Nothing is left running.

## settings.json

    "spawn": {
      "max_helpers": 8,
      "max_minutes": 5,
      "manager_model": "external/haiku-5-5",
      "helper_model": "external/haiku-5-5"
    }

Every key is optional. Without the section the harness uses 8 helpers, 5 minutes and the
default model.

## The trace

Every copy writes to the same trace.jsonl, under the session id of the chat that typed
`/spawn`, and under its own name as the agent. That is what lets the agent view draw one
row per agent.

| Line | Written by | Holds |
|---|---|---|
| `spawn` | the chat | the goal and `max_minutes` |
| `helper_start` | the manager | the helper's name and its task |
| `helper_report` | the manager | the helper's name, its exit code and its report |
| `spawn_report` | the chat | the goal and the manager's report |

The model calls and tool calls of each copy are traced as they already are.

## Rules

- A copy is a process, never a thread. One that fails or hangs is stopped without taking
  the chat down with it.
- A role changes four things about a copy and no more: its prompt, its model, the tools it
  gains and the tools it is refused. Keep them in one table in the code, one entry per role.
- No copy gets a tool the chat is denied. The deny list in settings.json holds for every
  copy.
- It imports only the standard library, plus what the harness already uses.
- The key in .env reaches a copy through the environment. It is never put in a task, a
  report or the trace.

## Test it

`tests/test_multiagent.py` checks what this file asks for. Run it by hand from the folder
that holds harness.py, with .venv-harness on:

    python tests/test_multiagent.py

It takes about a minute and makes a few real calls to the model, so it needs the key in
.env and, off campus, the UW VPN. It prints one line per check, then `ok`. A check that
fails prints one line that starts with `FAIL` and says what this file asks for. `/spawn`
is done when the test prints `ok`.

How it works: the test copies your harness into an empty temporary folder, starts it
there as a separate program, types `/spawn` into it, and reads what the run left behind.
Your own folder and your own trace.jsonl are never touched.

| What it does | What it checks |
|---|---|
| Reads the `COMMANDS` list. | `spawn` is in it. |
| Types `/spawn` with no goal. | It says how to use it and starts nothing. |
| Calls `start_helpers` with three tasks and `max_helpers` set to 2. | The chat does not have the tool. The call is refused, the answer names `max_helpers`, and no helper starts. |
| Starts one copy with `--role helper --task`. | It prints `=== report ===` and its report after it. |
| Types `/spawn` with a goal for three helpers. | The three files are made. The trace has the four lines above. The helpers work at the same moment. Every line carries its agent's name and the one session. The manager wrote no file. Nothing is left running. |
| Types `/spawn` with a long goal and `max_minutes` set to 0.2. | The run stops in well under a minute, the report says why, and no harness.py is left running. |

The first three rows need no model, so a build that is not there yet fails in a second.

A failure on the fifth row can be the model's choice and not your code: a manager may
start fewer helpers than the goal names. Run the test once more before changing anything.
