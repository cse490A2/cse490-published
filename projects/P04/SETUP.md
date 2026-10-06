---
title: "P04 setup"
parent: "P04"
grand_parent: "Projects"
nav_order: 1
permalink: "/projects/P04/setup/"
---

\# \*\*Project 4 setup guide\*\*

This week's setup is small. Project 4 continues in the Project 3 workspace, with the same harness, the same key and the same LiteLLM VSCode Chat extension. Nothing new is installed. If you ran \[the wizard\](https://canvas.uw.edu/courses/1916846/pages/course-setup-the-wizard) for Project 3, or followed the \[Project 3 setup guide\](../P03/SETUP.md) by hand, everything below is already in place.

\#\# \*\*What you already have\*\*

From the Project 3 setup, you need these things in place:

\* Your Project 3 project folder, with the \`harness.py\` you finished in Project 3\.  
\* The \`.env\` file in that folder, still holding your course key and the gateway address.  
\* The \`read\_file\` and \`write\_file\` tools your harness got in Project 3; the memory step writes \`memory.md\` with them.  
\* The chat extension, open in VS Code and pointed at the CSE 490 server.

If any is missing, the matching step of the Project 3 setup guide puts it back. The sections below say which step.

\#\# \*\*Mac\*\*

\#\#\# \*\*1\\. Project folder\*\*

Open your Project 3 project folder in VS Code: the folder that holds \`harness.py\`. The \`AGENTS.md\` you got with the Project 3 starter is already there; this week you rewrite it. The new \`skills/\` folder goes beside it in the same folder. If the folder is gone, "Project files" in the Project 3 setup guide gives you the starter again; your own harness changes come from your Project 3 submission.

\#\#\# \*\*2\\. Course key\*\*

Open \`.env\` in that folder. It holds these two lines from the Project 3 setup:

\`\`\`  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
\`\`\`

If the file is missing or the key line is empty, follow "Course key" in the Project 3 setup guide.

\#\#\# \*\*3\\. AI chat in VS Code\*\*

Open the chat panel: the speech-bubble icon at the top, or Ctrl+Cmd+I. Click the model picker at the bottom of the chat box and pick a course model under CSE 490\. If the CSE 490 server is not listed, follow "AI chat in VS Code" in the Project 3 setup guide. Keep the Project 3 setting that switches agent mode off (\`"chat.agent.enabled": false\`): the chat answers in text and you type every change into \`harness.py\` yourself, as the handout's prompts expect.

\#\#\# \*\*4\\. Harness check\*\*

Prove the harness runs and holds a conversation. In a terminal in your project folder:

\`\`\`  
python3 harness.py  
\`\`\`

Type a first message that gives it a fact, such as my name is Sam, and press Enter. Then ask what is my name? and press Enter. A reply that uses the name means the harness runs and holds a conversation, and the key and the gateway work. A reply that does not know the name means the harness is not keeping the context between turns; go back to the chatbot loop in the Reference of the \[Project 3 handout\](../P03/README.md). Then ask it to read \`hello\_world.py\`. A reply that quotes the file means the read tool from Project 3 is there. Press Ctrl+C to stop the harness.

If the harness stops before the model answers, prove the key on its own with "Model gateway" in the Project 3 setup guide (the curl command). A list of models means the key and address are right and the fault is in \`harness.py\`; an "invalid key" error means \`.env\` is wrong; redo step 2\. No response at all means a network problem; if it keeps happening, tell the course staff.

\#\# \*\*Windows\*\*

\#\#\# \*\*1\\. Project folder\*\*

Open your Project 3 project folder in VS Code: the folder that holds \`harness.py\`. The \`AGENTS.md\` you got with the Project 3 starter is already there; this week you rewrite it. The new \`skills/\` folder goes beside it in the same folder. If the folder is gone, "Project files" in the Project 3 setup guide gives you the starter again; your own harness changes come from your Project 3 submission.

\#\#\# \*\*2\\. Course key\*\*

Open \`.env\` in that folder. It holds these two lines from the Project 3 setup:

\`\`\`  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
\`\`\`

If the file is missing or the key line is empty, follow "Course key" in the Project 3 setup guide.

\#\#\# \*\*3\\. AI chat in VS Code\*\*

Open the chat panel: the speech-bubble icon at the top, or Ctrl+Alt+I. Click the model picker at the bottom of the chat box and pick a course model under CSE 490\. If the CSE 490 server is not listed, follow "AI chat in VS Code" in the Project 3 setup guide. Keep the Project 3 setting that switches agent mode off (\`"chat.agent.enabled": false\`): the chat answers in text and you type every change into \`harness.py\` yourself, as the handout's prompts expect.

\#\#\# \*\*4\\. Harness check\*\*

Prove the harness runs and holds a conversation. In PowerShell in your project folder:

\`\`\`  
python harness.py  
\`\`\`

Type a first message that gives it a fact, such as my name is Sam, and press Enter. Then ask what is my name? and press Enter. A reply that uses the name means the harness runs and holds a conversation, and the key and the gateway work. A reply that does not know the name means the harness is not keeping the context between turns; go back to the chatbot loop in the Reference of the \[Project 3 handout\](../P03/README.md). Then ask it to read \`hello\_world.py\`. A reply that quotes the file means the read tool from Project 3 is there. Press Ctrl+C to stop the harness.

If the harness stops before the model answers, prove the key on its own with "Model gateway" in the Project 3 setup guide (the curl.exe command). A list of models means the key and address are right and the fault is in \`harness.py\`; an "invalid key" error means \`.env\` is wrong; redo step 2\. No response at all means a network problem; if it keeps happening, tell the course staff.

\#\# \*\*Linux\*\*

\#\#\# \*\*1\\. Project folder\*\*

Open your Project 3 project folder in VS Code: the folder that holds \`harness.py\`. The \`AGENTS.md\` you got with the Project 3 starter is already there; this week you rewrite it. The new \`skills/\` folder goes beside it in the same folder. If the folder is gone, "Project files" in the Project 3 setup guide gives you the starter again; your own harness changes come from your Project 3 submission.

\#\#\# \*\*2\\. Course key\*\*

Open \`.env\` in that folder. It holds these two lines from the Project 3 setup:

\`\`\`  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
\`\`\`

If the file is missing or the key line is empty, follow "Course key" in the Project 3 setup guide.

\#\#\# \*\*3\\. AI chat in VS Code\*\*

Open the chat panel: the speech-bubble icon at the top, or Ctrl+Alt+I. Click the model picker at the bottom of the chat box and pick a course model under CSE 490\. If the CSE 490 server is not listed, follow "AI chat in VS Code" in the Project 3 setup guide. Keep the Project 3 setting that switches agent mode off (\`"chat.agent.enabled": false\`): the chat answers in text and you type every change into \`harness.py\` yourself, as the handout's prompts expect.

\#\#\# \*\*4\\. Harness check\*\*

Prove the harness runs and holds a conversation. In a terminal in your project folder:

\`\`\`  
python3 harness.py  
\`\`\`

Type a first message that gives it a fact, such as my name is Sam, and press Enter. Then ask what is my name? and press Enter. A reply that uses the name means the harness runs and holds a conversation, and the key and the gateway work. A reply that does not know the name means the harness is not keeping the context between turns; go back to the chatbot loop in the Reference of the \[Project 3 handout\](../P03/README.md). Then ask it to read \`hello\_world.py\`. A reply that quotes the file means the read tool from Project 3 is there. Press Ctrl+C to stop the harness.

If the harness stops before the model answers, prove the key on its own with "Model gateway" in the Project 3 setup guide (the curl command). A list of models means the key and address are right and the fault is in \`harness.py\`; an "invalid key" error means \`.env\` is wrong; redo step 2\. No response at all means a network problem; if it keeps happening, tell the course staff.

\#\# \*\*Claude Code, for the last step only\*\*

The last step of the handout copies your finished skill into \`.claude/skills/\` and runs it in Claude Code. Claude Code is not part of this week's setup. If you already have it, the \[Claude Code skills docs\](https://code.claude.com/docs/en/skills) say what the folder needs. Everything before that step runs in your own harness and the chat extension.  
