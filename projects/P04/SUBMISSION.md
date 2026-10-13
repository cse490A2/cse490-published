---
title: "P04 submission"
parent: "P04: Driving a Coding Agent"
grand_parent: "Projects"
nav_order: 2
permalink: "/projects/P04/submission/"
---

# Project 4 Submission

Push your harness repository to GitHub and submit its link to the Project 4 assignment in Canvas. Compare the repository with the tree below first. Leave out your .env file.

## What the repository holds

* harness.py  
* HARNESS.md  
* PLAN.md  
* skills/coding-loop/SKILL.md  
* the task code from the starter: inbox.jsonl, detector.py, score.py  
* transcript.md

## What each file is

* harness.py: your Project 3 harness after the three changes the handout's Part 1 asks of the LiteLLM chat extension.  
* HARNESS.md: your agent's standing rules, the file it reads in place of its built-in system prompt.  
* PLAN.md: the plan your agent wrote in plan mode for the job, before you typed approve.  
* skills/coding-loop/SKILL.md: the course's skill, copied from the starter, unchanged.  
* detector.py: the task code after your agent's change; inbox.jsonl and score.py as the starter shipped them.  
* transcript.md: the session your agent saved: the job, the plan, approve, every file it wrote, every validation run, the report.

## What to leave out

Leave out your .env file and the logs/ folder VS Code wrote in Project 3\. A .env file or a key in the repository costs the clean-repo check and is reported to you by name.

## How to submit

Push the repository with git push. Open it on GitHub and check that the six items above are there. Paste the repository's address into the Project 4 assignment in Canvas and submit. Fill out the feedback form.

## The examples

The [published examples](https://github.com/cse490A2/cse490-published/tree/main/projects/P04/examples) hold a HARNESS.md written the way Claude Code's own example is, and a transcript.md from one run of the coding-loop skill on the starter.  
