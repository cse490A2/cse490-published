---
title: "P06: Fixing Code You Did Not Write"
parent: "Projects"
nav_order: 6
has_children: true
permalink: "/projects/P06/"
---

# Project 6: Fixing Code You Did Not Write

**Due: Tuesday 11:59 pm**  
Prerequisites: run the course setup wizard during class.  
In this project, you’ll fix errors in a real production system – [thumbor](https://www.thumbor.org), via GitHub (working in your own branch).  You’ll start by equipping your harness with the ability to interact with GitHub. You’ll use your harness to pull a repository, identify issues, and develop strategies to fix bugs while manually reviewing changes made. The intent of this project is to demonstrate common software engineering practices for working in a shared repository using agents. 

## Instructions

1. We will be using [thumbor](https://www.thumbor.org) as our target repo for bug fixing. Thumbor is an image processing service that can manipulate images automatically based on user specification through a URL. From the setup instructions, you already have your own private copy of thumbor under your GitHub account, as it was in September 2026 before four of these five bugs were fixed in the real project, plus one feature that does not exist yet. The five are filed as issues in your copy.   
   1. Familiarize yourself with thumbor. You can have a conversation with AI, or briefly read the [documentation](https://thumbor.readthedocs.io/en/latest/). Follow the [getting started](https://thumbor.readthedocs.io/en/latest/getting_started.html) instructions (without pip installing) to understand how to use thumbor to manipulate images.  
   2. Below shows an overview of the bugs targeted to be fixed. These were pulled by real issue reporting from previous versions. The issues in your repository carry the conversation from the real thumbor reports. 

| In your repo | Issue \# | Issue | What you see | What you should see | CHECK URL |
| :---- | :---- | :---- | :---- | :---- | :---- |
| \#2 | [\#1687](https://github.com/thumbor/thumbor/issues/1687) | Transparent rounded corners have a dark ring | A thin dark outline along the curve in the image’s corner | The corner fades into the page with no outline | `/unsafe/300x200/filters:round_corner(60,255,255,255,1):format(png)/example.jpg` |
| \#3 | [\#1886](https://github.com/thumbor/thumbor/issues/1886) | Resized GIF loses its transparent background | A black box surrounds a GIF | The GIF with nothing around it | `/unsafe/240x160/sticker.gif` |
| \#4 | [\#1711](https://github.com/thumbor/thumbor/issues/1711) | Very wide and very short resizes comes back empty | A blank 800 by 20 image, nothing visible | A rainbow strip 800 pixels wide and 20 tall | `/unsafe/800x20/rainbow.png` |

2. You will use your harness to fix these through the GitHub MCP server. The GitHub MCP server equips your agent. The setup guide put the GitHub MCP server beside your harness; step 3 connects it.  
3. Your harness can talk to GitHub through MCP, but it needs to know how to interact with the environment. Add the following tools to your harness.py by asking the LiteLLM chat in VS Code   
   1. Your harness may already have some of the tools in the table below; add any that are missing. As we add more capabilities to your harness, some tools may need to grow with them. Check to ensure the following tools have the capabilities from the spec. Use LiteLLM Chat to generate code if needed.

| Tool Name | Purpose | Spec |
| :---- | :---- | :---- |
| MCP servers | Generalize to list out available MCP servers | At startup, connect to every MCP server in the mcpServers section of settings.json and offer their tools beside the file tools. Write the full tool list, by name, as the first line of course/trace-build.jsonl inside the working folder, and append every call and its reply to it; the file grows for the life of the branch and is never rewritten. |
| `execute_file`(shell) | Execute a file from the provided shell command | `execute_file` runs a shell command in the working folder, with the folder's venv on the path if it has one, and returns stdout, stderr and the exit code. |
| Git gate | Security layer for detecting dangerous command | Before `execute_file` runs a git command, check it against the deny list in the permissions section of settings.json and refuse any command that matches, saying which entry; refuse any tool call whose name is on that list the same way. |

   2. The table below are new tools your agent will need to interact with GitHub MCP. Paste each row's Spec cell to the LiteLLM chat as its own prompt, in table order, and read each change before you accept it:

| Tool Name | Purpose | Spec |
| :---- | :---- | :---- |
| GitHub Working folder | Point the harness at a GitHub repository | The harness takes a folder as its command-line argument and treats it as the repository. Every file path and every command is relative to that folder. |
| Repository instructions | Let the model read the repository's own instructions for running and testing it | At startup, if the working folder has an AGENTS.md, put its contents into the context before the first turn. |
| `edit_file` | Change one passage without rewriting the file | Add `edit_file`. It takes a file path, an exact old passage and a new passage. It replaces the one occurrence and fails if the passage occurs zero times or more than once. |

   3. Check it: run harness.py with the Python from the setup guide's harness step, pointed at p06-\<your login\>, and ask it "List the open GitHub issues of this repository." Your open issues back means GitHub is connected: .env holds your token, so there is nothing to sign into.  
4. Use your harness to fix the three issues listed in step 1, one at a time. If you have not already, start the image server with the command in AGENTS.md and open each CHECK URL on it to see the bug. Follow below for each while, while changing “N” to the issue number to be worked on.:  
   1. Make a branch for it: "Update main, then create a branch named issue-N from it."   
   2. Have your harness reproduce the bug: "Read issue \#N. Write one test that fails for the reason the issue describes, and run it to see it fail."  
   3. Have it fix the bug: "Fix issue \#N as it describes and nothing more. Run the test again, then the whole suite, with the repository's own Python environment."  
   4. Check the picture yourself: restart the image server and open the table's URL and every URL in the issue's text; an issue can have more than one symptom, and the table shows one.   
   5. Check that only the issue's code changed and nothing else: "Show the git diff against main, leaving out course/trace-build.jsonl, and confirm only the files for issue \#N and the new test changed." If it changed more, have your harness undo that part.  
   6. Commit the fix and the trace with a message that names the issue, and push the branch (if your harness already committed, this commits only what is left): "Commit the fix, the test and course/trace-build.jsonl with a message that names the issue, and push the branch."  
5. Even though your repository is a private copy, open a pull request for each branch to simulate pushing the fix to the team's main branch.  
   1. Instruct your harness: "Open a pull request from issue-N against main. Leave the description empty; I will write it myself."  
   2. Review it on the pull request page, the way a teammate would: read the changed files and the new test, and leave one comment in your own words on what the change does, as a GitHub review with a comment or as a comment on the conversation; either counts. If a mistake is found, have your harness fix it and push the branch again.   
   3. Write the description yourself: the issue, every source file changed, and which AI tools you used.  
   4. When the checks on the page are green, merge it; they can take ten minutes. The main repo now includes your fix.

## Turnin

Submit on the Project 6 assignment in Canvas, by Tuesday 11:59 pm: 

* The link to your repository, https://github.com/\<your login\>/p06-\<your login\>, as the text entry. 

## Grading

A model will autograde your submission. For each of the three pull requests it checks that the suite passes, your new test fails before your change and passes after it, the files the issue needs are changed, your review comment is on the pull request, the description is in your words and names the issue, the files and the AI tools you used, and the trace matches the diff. Every check is pass or fail. Merging the pull request does not change the grade. It does not judge code style, prompt wording, or how many tries it took.

## Reference

Out of bounds: changes the issue did not ask for, dependency upgrades, force-pushes, pushing straight to main, editing the repository by hand, and a pull request description the agent wrote. Any mix of asking your agent and steering it is fine. The trace has to be the true story of that mix.  
