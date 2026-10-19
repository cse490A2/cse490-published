---
name: plan-mode
description: Use when a message starts with /plan, or when the coding-loop skill decides a job needs a plan.
---

# plan-mode

Read and ask. Change nothing until the user types approve.

1. Read the files the job names, with read_file only.
2. Ask the user what you need to know, one question at a time, and wait for each answer. Four questions at most.
3. Write PLAN.md with write_file: the decisions from the answers, the files you will change, what each change does, and how the score will show it worked. Overwrite the last plan.
4. Say "waiting for approve" and stop.
5. Make no other write_file call and no execute_file call before the user types approve. After approve, continue the job.
