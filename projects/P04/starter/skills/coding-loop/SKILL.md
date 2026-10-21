---
name: coding-loop
description: Use when a message asks to fix, add, change, build or improve code, or to make a program pass its score or tests.
---

# coding-loop

Spec, decision, change, score, again. Each step leaves something a reader can check.

1. Read the code the job names, SPEC.md, and a few files in articles/.
2. Decide whether the job needs a plan. A new program, or a change to how code behaves, does. A comment, a rename, or a one-line fix does not. Say which and why in one line.
3. If it needs a plan: read skills/plan-mode/SKILL.md with read_file and follow it. Continue here after the user types approve.
4. Make the change one file at a time with write_file. Say what changed and why, one line per file.
5. The harness runs python pedia.py score after every write and sends you the output. pedia.py is the program this project builds, to SPEC.md; it does not exist until your first write creates it, and until then the harness says so instead of a score. Read which questions were missed. Do not run score yourself.
6. If the score is below the target, change the ranking for what the missed questions need and go back to step 4. Stop after three rounds and say what is still missing.
7. Write the tests the job asked for, in tests/, before you report: one test per command and one per profile key.
8. Report: the score line, the files you wrote, and what you would try next.
9. Append a section to transcript.md, headed with the job: the decision from step 2, the questions and answers, PLAN.md if you wrote one, the approve, every write_file call with its full content, every score line, and the report.
