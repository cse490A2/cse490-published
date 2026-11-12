# TOOLS.md: the tools to add to this harness

A tool is one Python function in harness.py. It sits in the local tools section, above the
line that starts `LOCAL_TOOLS =`. Its name is added to that list. Nothing else changes.

    def word_count(path: str) -> str:
        """Count the words in a file.

        Args:
            path: Path of the file to count.
        """
        return str(len(read_file(path).split()))


    LOCAL_TOOLS = [read_file, write_file, execute, use_skill, word_count]

The harness builds what the model sees from the function itself:

| The model sees | The harness takes it from |
|---|---|
| The tool's name | The function's name |
| What the tool does | The docstring, up to `Args:` |
| The arguments | The function's own parameters |
| What each argument is | Its line under `Args:` |

So the docstring is written for the model. Say what the tool does and when to use it. An
argument with no line under `Args:` is described by its name alone.

## The eight tools

| Tool | Arguments | Returns |
|---|---|---|
| fetch_url | url | The page as plain text. Tags are removed, and so are the contents of style and script elements. The text is cut at 8,000 characters. |
| remember | text | Appends the text as one line to MEMORY.md in the working folder. Returns the number of lines the file now has. |
| todo | items | Writes todo.md as a checklist and returns it. `items` is text with one item per line. A line that starts with `[x]` is done. Any other line is open. |
| find_text | text | Every file and line in the working folder that contains the text, as `path:line: text`. It skips trace.jsonl, the .undo folder and every folder whose name starts with a dot. It cuts a line at 300 characters and stops at 200 matches. |
| undo | path | Puts the file back from its copy under .undo/ and returns the path it restored. |
| diff | path | A unified diff of the file against its copy under .undo/. |
| cost | none | A table of model calls, tokens and cost per agent and per model, summed from the `model_call` lines of trace.jsonl. A line with tokens and no cost still counts. |
| summarize | path | The file's content in five lines, from the model. |

Three of these need more than a new function:

- undo and diff read a copy that nothing keeps yet. Change `write_file` so it copies the
  file to `.undo/<the same path>` before it writes. A file that did not exist has no copy.
- cost reads trace.jsonl, so trace.py has to be beside harness.py. Without a trace it
  returns `Error: no trace.jsonl yet`.
- summarize asks the model through the harness's own `call_model`, with one message and no
  tools. It never builds a request of its own, never opens .env and never names a model.

## Rules every tool follows

- Every argument is a string, and the tool returns a string.
- A path goes through `checked(path)` before the tool opens it. That refuses a path outside
  the working folder, and it refuses .env.
- A tool may raise an error. The harness turns it into `Error: ...` and gives that to the
  model. A tool that handles a failure itself returns text that starts with `Error:`.
- It imports only the standard library plus requests.
- Its name is not one the harness already has: read_file, write_file, execute, use_skill,
  and the names the MCP servers add (the startup line of trace.jsonl lists them).
- It stays under about 40 lines.

## One tool at a time

Every tool is in the same file, and `write_file` replaces a whole file. Two agents that
change harness.py at the same moment lose one agent's work. Add the tools one after
another, or give each agent a turn.

## Tests

Each tool has its own test, already written: `tests/test_<tool_name>.py`. The tests folder
comes in p07/. Move it beside harness.py, because the `execute` tool only runs a file inside
the working folder.

| File | What it checks |
|---|---|
| tests/test_fetch_url.py | Tags, style and script are gone. The text is cut at 8,000 characters. |
| tests/test_remember.py | One line per call in MEMORY.md, and the line count returned. |
| tests/test_todo.py | todo.md as a checklist, with done and open items. |
| tests/test_find_text.py | The `path:line: text` form, the skipped files and the two limits. |
| tests/test_undo.py | `write_file` keeps the copy, and undo puts it back. |
| tests/test_diff.py | A unified diff, with the copy as the old side. |
| tests/test_cost.py | The sums per agent and per model, and the answer with no trace. |
| tests/test_summarize.py | Five lines, from one call through `call_model` with no tools. |

A test is a plain Python script. Run it with the `execute` tool, or by hand from the folder
that holds harness.py:

    .venv-harness/bin/python tests/test_fetch_url.py

A test passes when it prints `ok` and exits with 0. A test that fails prints one line that
starts with `FAIL` and says what TOOLS.md asks for. A tool is done when its own test prints
`ok`.

- Every test calls its tool the way the model does, so it also fails when the name is
  missing from `LOCAL_TOOLS`.
- Every test works in an empty temporary folder. It never writes the real MEMORY.md, todo.md
  or trace.jsonl.
- The test for summarize makes one real call to the model. It needs the key in .env and,
  off campus, the UW VPN.
- tests/toolcheck.py is shared by the tests. Leave the tests as they are: change the tool
  until its test passes.

To try a tool by hand:

    .venv-harness/bin/python -c "import harness; print(harness.fetch_url('https://example.com'))"

## When a test fails

Read what the test printed before changing anything. What it printed says whose fault the
failure is:

| The test printed | Cause | What to do |
|---|---|---|
| `FAIL test_<tool_name>.py: ...` | The tool does not do what this file asks. | Change the tool so the sentence after `FAIL` is true. Run the test again. |
| A `got:` line that holds `GatewayError` | The model could not be reached. The tool may be right. | Stop. Report it. Do not change the tool. |
| `FAIL ... .env beside harness.py needs ...` | The key is missing. The tool may be right. | Stop. Report it. Do not change the tool. |
| A traceback that ends in `SyntaxError`, or any other error from `import harness` | harness.py no longer loads, so no test can run. | Mend the line the traceback names. Then run the test again. |
| `Error: still running after ... seconds` | The test ran past the limit of the `execute` tool. | The tool waits on something. Give its request a timeout. |

The line under `FAIL` that starts with `got:` shows what the tool returned.

Try a tool three times at most. A try is one change to the tool and one run of its test.
After the third failed run, stop and leave the tool as it is.

Never change a test, and never change toolcheck.py, to get `ok`. Never take another tool
out of `LOCAL_TOOLS` to mend your own.

When you stop, with `ok` or without, your report says three things:

- The tool's name.
- `ok`, or the last line the test printed, word for word.
- For a tool that is not done, what you tried.

A tool with no `ok` is not done. Say so plainly. A report that leaves the failure out costs
more than the failure.
