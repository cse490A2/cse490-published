---
title: "P04: Driving a Coding Agent"
parent: "Projects"
nav_order: 4
has_children: true
permalink: "/projects/P04/"
---

# Project 4: Driving a Coding Agent

Due: Tuesday 11:59 pm  
Before class, check that your Project 3 harness runs and read files.  
Last week you built the loop. This week you hire it. Keep building the harness you wrote in Project 3 and turn it into a coding agent: give it standing rules, a plan mode, and one skill, then hand it a coding job and steer. You write no harness code yourself. Every change to harness.py is a prompt to the LiteLLM chat in VS Code, as in Project 3, and your agent runs on external/haiku-4-5-20251001 through the course gateway.

## Instructions

### Part 1: the files

1. Write your agent's standing rules in a file of its own. Make HARNESS.md in your harness repo: what the agent edits without asking and what it asks you before doing, written the way [Claude Code's example CLAUDE.md in the Best practices reading](https://code.claude.com/docs/en/best-practices#write-an-effective-claude-md) is. The AGENTS.md already in the repo governs the chat in VS Code; leave it alone. Then ask the LiteLLM chat to load yours in place of the built-in system prompt with the following prompt:  
   1. "Read harness.py. Replace SYSTEM\_PROMPT with the text of HARNESS.md, read once when the program starts. Change nothing else."  
   2. Check it: start the harness and ask what its rules are. The reply quotes HARNESS.md.  
2. Add a plan mode. Ask the LiteLLM chat for it with the following prompt:  
   1. "Read harness.py. Add a plan mode. When my message starts with /plan, the model may call read\_file and ask me questions, but the harness refuses write\_file and execute\_file and says so. The model ends the plan by writing its steps to PLAN.md. The harness allows write\_file and execute\_file again only after I type approve. Change nothing else."  
   2. Check it: send "/plan: add a comment line to hello\_world.py". The harness refuses the write and says so, and PLAN.md appears. Type approve. The edit lands.  
3. Add the course's skill. The starter ships skills/coding-loop/SKILL.md: the skill that drives the agentic coding loop. Its steps: take the job as a /plan message, write the plan, wait for approve, make the change, run the validation, report the result and save transcript.md with every file it wrote. It has three parts: the skill's name, one line saying when to use it, and those steps. Copy the skills/ folder from [the starter](https://github.com/cse490A2/cse490-published/tree/main/projects/P04/starter) into your harness repo and read SKILL.md once. Part 2 runs it.  
4. Ask the LiteLLM chat to make your harness load the skill when a message calls for it with the following prompt:  
   1. "Read harness.py. At startup, read every skills/\*/SKILL.md and keep each one's name and when-to-use line in the context. When my message matches a when-to-use line, add that skill's full text to the context for that turn. Change nothing else."  
5. Check it: send "/plan fix the failing test in hello\_world.py", a job the when-to-use line matches. The reply is in plan mode: it asks you a question or writes PLAN.md, and it edits nothing. Then send "what time is it". The reply names no skill and no plan. The grader reads the same two exchanges in transcript.md and the scan-and-match code in harness.py.

### Part 2: the job

1. Pull [the test code](https://github.com/cse490A2/cse490-published/tree/main/projects/P04/starter) into your harness repo's folder. Use your agent to drive the coding loop on it: send the job as a /plan message, answer the plan's questions, type approve when the plan would work, and interrupt when it drifts. The skill runs the validation and writes transcript.md. The starter names the job, its validation, and the number to beat.

## Turnin

By Tuesday 11:59 pm:

* Push your harness repo with harness.py, HARNESS.md, PLAN.md, the skills/ folder, the task code, and transcript.md. Leave out your .env file.  
* Submit the repository link to the Project 4 assignment in Canvas. Compare your files with [the examples](https://github.com/cse490A2/cse490-published/tree/main/projects/P04/examples) first.  
* Fill out the feedback form.

## Grading

A model will autograde your submission. It reads your repository and checks that each step was properly followed. Every check is pass or fail. It does not judge code style or prompt wording. It checks five behaviors, and that the files the Turnin list names are present and clean. HARNESS.md enters the context before the loop, in place of the built-in system prompt. Plan mode refuses edits until approve and writes PLAN.md first. The skill's full text enters the context only on a matching message. The validation passes on [the starter](https://github.com/cse490A2/cse490-published/tree/main/projects/P04/starter)'s public cases and on a second set you cannot see. transcript.md shows the skill's steps in order: plan, approve, change, validation. The three check it lines in Part 1 are these same checks, read from harness.py and transcript.md. Code that memorizes the public cases loses on the hidden ones. Hand-written task code costs the delegation checks.  
