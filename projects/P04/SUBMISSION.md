---
title: "P04 submission"
parent: "P04: Driving a Coding Agent"
grand_parent: "Projects"
nav_order: 2
permalink: "/projects/P04/submission/"
---

# Project 4 Submission

In VS Code, open the Command Palette (Cmd+Shift+P on Mac or Ctrl+Shift+P on Windows) and run CSE 490: Package for turn-in. It writes P04-submission.zip in your Project 3 folder. Upload that file to the Project 4 assignment in Canvas. Compare the zip with the tree below first.

## What the zip holds

* harness.py  
* systemprompt.md  
* PLAN.md  
* skills/plan-mode/SKILL.md and skills/coding-loop/SKILL.md  
* explain.py and tests/  
* transcript.md  
* logs/, the chat log VS Code kept

## What each file is

* harness.py: your Project 3 harness after the three changes the handout's steps 3 and 5 ask of the LiteLLM chat: the skills scan at startup, the match on each message, and the hook that runs the score after every write.  
* systemprompt.md: the starter's five parts with your two rules under Your rules.  
* PLAN.md: the plan your agent wrote last, before you typed approve.  
* skills/: the two skills as the starter shipped them, unchanged.  
* explain.py and tests/: the product your agent built in step 7, as its last write left them.  
* transcript.md: the sections your agent appended, one per job: the decision, the questions and answers, the plan, the approve, every file it wrote, every score line, the report.  
* logs/: the record of your prompts to the LiteLLM chat. Leave it as it is.

## What to leave out

The package command leaves out .env on its own; snippets/ rides along and is fine. A key anywhere in the zip costs the rules check and is reported to you by name.  
