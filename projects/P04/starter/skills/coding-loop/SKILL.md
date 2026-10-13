---
name: coding-loop
description: Drive a coding job from plan to validated change. Use when a message starts with /plan, or asks to fix, add, change or improve code, or to make the detector beat the target.
---

# coding-loop

The steps, in order. Each one leaves something a reader can check.

1. Take the job as a /plan message. If it did not arrive as one, ask the user to send it as /plan.
2. In plan mode, read the files the job names and ask the user what you need to know. Write your steps to PLAN.md: the files you will change, what each change does, and how the validation will show it worked.
3. Wait for the user to type approve. Change nothing before that.
4. Make the change, one file at a time, with write_file. Say what changed and why in one line per file.
5. Run the validation with execute_file: python3 score.py. Read its output.
6. If the score is below the target, go back to step 4 with what the misses show. Stop after three rounds and say what is still wrong.
7. Report the result: the score line, the files you wrote, and what you would try next.
8. Save transcript.md in the project folder: the /plan message, your questions and the answers, PLAN.md, the approve, every write_file call with its full content, every validation run with its output, and the report.
