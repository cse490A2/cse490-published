---
title: "P04 submission"
parent: "P04"
grand_parent: "Projects"
nav_order: 2
permalink: "/projects/P04/submission/"
---

\# Project 4 Submission

Zip \`harness.py\`, \`AGENTS.md\`, and your \`skills/\` folder as \`P04-submission.zip\`. Compare the zip with the tree below. Upload it to the Project 4 assignment in Canvas by Tuesday 11:59 pm.

\#\# What the zip holds

\`\`\`  
P04-submission.zip  
    harness.py  
    AGENTS.md  
    skills/  
        \<your-skill\>/  
            SKILL.md  
            memory.md  
            transcript.md  
            \<your-subskill\>/  
                SKILL.md  
\`\`\`

\`\<your-skill\>\` and \`\<your-subskill\>\` are the folder names you chose. Name the skill folder for your skill, the same name your \`SKILL.md\` gives it, and name the subskill folder with the name the parent skill's step uses for it. Everything else is named as written here.

| File | What it is |  
|---|---|  
| \`harness.py\` | Your Project 3 harness after the changes the handout's Instructions ask of the LiteLLM chat extension. |  
| \`AGENTS.md\` | Your agent's standing rules: what it may do on its own and what it asks you first. |  
| \`skills/\<your-skill\>/SKILL.md\` | The skill's name, one line saying when to use it, and its steps, as the handout describes them. |  
| \`skills/\<your-skill\>/\<your-subskill\>/SKILL.md\` | The step you moved out of the parent skill, with its own steps. |  
| \`skills/\<your-skill\>/memory.md\` | What your agent wrote after each of the two uses. |  
| \`skills/\<your-skill\>/transcript.md\` | One real session of your own work, saved by your agent. |

\#\# What to leave out

Leave out your \`.env\` file and the \`logs/\` folder that VS Code wrote in Project 3\. The commands below name only \`harness.py\`, \`AGENTS.md\`, and \`skills\`, so both stay out on their own. Check that no key sits inside \`harness.py\` or your skill's folder: your course LiteLLM gateway key lives in \`.env\` and nowhere else.

\#\# How to make the zip

Open a terminal in the folder that holds \`harness.py\` (in VS Code: Terminal, then New Terminal) and run the line for your machine.

macOS:

\`\`\`  
zip \-r P04-submission.zip harness.py AGENTS.md skills \-x '\*.DS\_Store'  
\`\`\`

Windows, in PowerShell:

\`\`\`  
Compress-Archive \-Path harness.py, AGENTS.md, skills \-DestinationPath P04-submission.zip  
\`\`\`

Before you upload, open the zip and compare it with the tree above. On macOS, \`unzip \-l P04-submission.zip\` lists what is inside. On Windows, double-click the zip in File Explorer.

\#\# The examples

The published examples at https://github.com/cse490A2/cse490-published/tree/main/projects/P04/examples are the weekly meal plan skill, published as five files in one folder. The example's files map onto the tree above like this. \`AGENTS.md\` sits at the top next to \`harness.py\`. \`SKILL.md\`, \`memory.md\`, and \`transcript.md\` sit in \`skills/meal-plan/\`. \`shopping-list-SKILL.md\` is the subskill and sits at \`skills/meal-plan/shopping-list/SKILL.md\`. The examples hold no \`harness.py\`. Yours is the one you built in Project 3\.  
