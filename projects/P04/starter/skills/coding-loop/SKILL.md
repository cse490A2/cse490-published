---
name: coding-loop
description: Use when a message asks to fix, add, change, build or improve code, or to make a program pass its score or tests.
---

# coding-loop

Spec, decision, change, score, again. Each step leaves something a reader can check.

1. Read the code the job names, SPEC.md, and a few files in snippets/.
2. Decide whether the job needs a plan. A new program, or a change to how code behaves, does. A comment, a rename, or a one-line fix does not. Say which and why in one line.
3. If it needs a plan: read skills/plan-mode/SKILL.md with read_file and follow it. Continue here after the user types approve.
4. Make the change one file at a time with write_file. Say what changed and why, one line per file.
5. The harness runs python explain.py score after every write and sends you the output. Read which facts were missed. Do not run score yourself.
6. If the score is below the target, add the construct the misses name and go back to step 4. Stop after three rounds and say what is still missing.
7. Report: the score line, the files you wrote, and what you would try next.
8. Append a section to transcript.md, headed with the job: the decision from step 2, the questions and answers, PLAN.md if you wrote one, the approve, every write_file call with its full content, every score line, and the report.
