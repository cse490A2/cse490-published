---
title: "P04: Driving a Coding Agent"
parent: "Projects"
nav_order: 4
has_children: true
permalink: "/projects/P04/"
---

# Project 4: Driving a Coding Agent

Due: Tuesday 11:59 pm  
Before class, run the setup wizard or the setup guide: it makes your Project 4 folder, a copy of your Project 3 folder with this week's files placed over it. Check that your harness runs and reads files.  
Last week you built the loop. This week you hire it. Keep building the harness you wrote in Project 3 and turn it into a coding agent: give it standing rules, two skills, and a hook, then hand it a coding job and steer. You write no harness code yourself. Every change to harness.py is a prompt to the LiteLLM chat in VS Code, as in Project 3, and your agent runs on external/haiku-5-5 through the course gateway.

## Instructions

### Part 1: the files

1. Give your agent its rules. systemprompt.md is the first message in every request your harness sends. systemprompt.md should now have multiple points for your instruction to follow. Change one thing: the two placeholder lines under Your rules, each written like the Constraints, "Never ..." or "Ask before ...", for something that went wrong last week. Feel free to adjust these lines to whatever works best for your agent.   
   1. Similarly to Project 3, the system prompt should be loaded with every user message.  
2. Add a skill. Alter your harness to load skills from skills/\<name\>/SKILL.md. Prompt the LiteLLM Chat:  
   1. "Read harness.py. At startup, have it read every skills/\*/SKILL.md and keep each one's name and its description line, the when-to-use line that starts with Use when, in the context. Change nothing else."  
   2. "Read harness.py. On each user message, if it matches a skill's description line, its when-to-use line, add that skill's full text to the context for that turn only. Change nothing else."  
   3. Check it: restart and ask your harness "what skills do you have". It should respond with plan-mode and coding-loop.  
3. Manually read the two skills in skills/ once, so you know what your agent will do. plan-mode reads and asks, writes PLAN.md, and changes nothing until you type approve; start a message with /plan to invoke it yourself. coding-loop is the loop from lecture; it decides whether a job needs a plan.  
4. Add a hook: code the harness runs at a fixed point in the loop without asking the model. Your yes before each command is one; this one runs after every write. Prompt the LiteLLM chat:  
   1. "Read harness.py. After every write\_file the harness runs, run python pedia.py score with the same Python that runs the harness, and add its output to the context as a message from the harness. If pedia.py does not exist yet, add a line saying so. Change nothing else."  
5. Test your harness with two messages:   
   1. "Delete the articles folder": it asks you first, and nothing happens until you answer.   
   2. "what time is it": no skill is named.   
   3. If a test fails, redo the step that built it, then repeat the test.  
6. Now put it all together. Have your agent build pedia.py, a search over the thousand Wikipedia articles in articles/, shaped to you. Send: "Read SPEC.md and build pedia.py to it. Standard library only." It says this needs a plan and asks two questions: which subjects win a tie, and how many results to show. Answer, read PLAN.md, type approve. Then watch the score after each write until it prints PASS; the misses it lists are what the next write fixes.  
7. Try it. Run python pedia.py search with something you have wondered about this week, then python pedia.py score.  
8. \[OPTIONAL\] To make your program awesome, add a read command that shows an article the way you like to read: the first paragraph, the Simple English version, or related articles after it.

## Turnin

By Tuesday 11:59 pm:

* Push your harness repo with harness.py, systemprompt.md, PLAN.md, profile.json, the skills/ folder, pedia.py, tests/, and transcript.md. Leave out your .env file and the articles folder.  
* Submit the repository link to the Project 4 assignment in Canvas.

## Grading

A model will autograde your submission. It reads your repository and checks that each step was properly followed, five checks, pass or fail, 20 points each. Rules: two rules of your own under Your rules, and your agent asked you before deleting the articles folder. Skills: harness.py reads every SKILL.md at startup and adds the full text only on a match. Plan: PLAN.md and your approve came before the first edit to pedia.py. Validation: pedia.py score passes on the public questions and on questions you cannot see, and a score run follows every write. Delegation: every file in pedia.py and tests/ came from a write\_file call in transcript.md. It does not judge code style, prompt wording, or how many tries it took.

## Reference

Switching the harness to Qwen: internal/Qwen3.6-35B-A3B costs nothing. Add this field to the JSON body of every request your harness sends, beside "model" and "messages": "extra\_body": {"chat\_template\_kwargs": {"enable\_thinking": false}}. Then set "model" to "internal/Qwen3.6-35B-A3B". If you run out of credits on Haiku, this is the switch.