---
title: "P02 setup"
parent: "P02: Insert Prompt to Play"
grand_parent: "Projects"
nav_order: 1
permalink: "/projects/P02/setup/"
---

# Project 2 setup guide

This document provides instructions to set up your environment for CSE490's in-class projects, starting with Project 2\.  See below for Mac, Windows, and Linux instructions (choose based on your machine/OS type).

## Mac

### 1\. Project folder

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P02/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week. It holds PROMPT.md, SCORECARD.md, an artifacts folder for the games the models write, and a logs folder for your chat log. Inside it, create a file named exactly .env: any text editor will do, or, once the folder is open in VS Code, right-click the folder name in the Explorer and choose New File. Paste these two lines into it:  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-1.png)  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. VS Code

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Open the downloaded file. Drag Visual Studio Code into Applications. Open it once so macOS trusts it. VS Code is installed when it opens to its welcome page.

### 3\. AI chat in VS Code

Install two extensions. In VS Code, open the Extensions panel: the four-squares icon on the left, or Cmd+Shift+X. Search for LiteLLM and install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan. Then download the course extension, CSE 490 Course Tools, as cse490-tools.vsix from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix. Back in the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. That extension keeps the chat log described in step 4 and packages your turn-in.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-2.png)  
Point it at the course gateway. Open the Command Palette (Cmd+Shift+P). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key. Switch agent mode off; this week the AI answers in chat and you save every file yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Cmd+I). Click the model picker at the bottom of the chat box; it reads Auto until you choose. Under CSE 490 you should see external/zai.glm-5, external/haiku-4-5-20251001 and internal/Qwen3.6-35B-A3B. Pick one before you send a message. If they are not listed, click "Manage Models...", then "Add Models", then "LiteLLM", choose the CSE 490 server, and tick the three. If any of them is still missing, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-3.png) ![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-4.png)

### 4\. Open the project

In VS Code, choose File, then Open Folder, and pick the starter folder. Save every game the models write into its artifacts folder, named the way artifacts/README.md says: the game name, one underscore, the model's short name, then .html. The course extension from step 3 sees logs/\_chatlog.json and, from then on, saves every chat you have with the course models in this folder to logs/\_chatlog.md, where you can read it any time. The status bar shows "Chat log" with the number of turns saved. The log stays on your computer. Nobody on the course staff sees it unless you turn it in, and it never includes your API key. To stop the log, delete logs/\_chatlog.json.

### 5\. Model gateway

Prove the key works. Open a terminal inside VS Code (menu Terminal, then New Terminal; it opens in your project folder) and run:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://llmproxy.cs.washington.edu/v1/models  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-5.png)  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## Windows

### 1\. Project folder

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P02/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week. It holds PROMPT.md, SCORECARD.md, an artifacts folder for the games the models write, and a logs folder for your chat log. Inside it, create a file named exactly .env: any text editor will do, or, once the folder is open in VS Code, right-click the folder name in the Explorer and choose New File. Paste these two lines into it:  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-6.png)  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. VS Code

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Run the installer. The defaults are fine. VS Code is installed when it opens to its welcome page.

### 3\. AI chat in VS Code

Install two extensions. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X. Search for LiteLLM and install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan. Then download the course extension, CSE 490 Course Tools, as cse490-tools.vsix from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix. Back in the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. That extension keeps the chat log described in step 4 and packages your turn-in.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-7.png)  
Point it at the course gateway. Open the Command Palette (Ctrl+Shift+P). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key. Switch agent mode off; this week the AI answers in chat and you save every file yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). Click the model picker at the bottom of the chat box; it reads Auto until you choose. Under CSE 490 you should see external/zai.glm-5, external/haiku-4-5-20251001 and internal/Qwen3.6-35B-A3B. Pick one before you send a message. If they are not listed, click "Manage Models...", then "Add Models", then "LiteLLM", choose the CSE 490 server, and tick the three. If any of them is still missing, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-8.png) ![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-9.png)

### 4\. Open the project

In VS Code, choose File, then Open Folder, and pick the starter folder. Save every game the models write into its artifacts folder, named the way artifacts/README.md says: the game name, one underscore, the model's short name, then .html. The course extension from step 3 sees logs/\_chatlog.json and, from then on, saves every chat you have with the course models in this folder to logs/\_chatlog.md, where you can read it any time. The status bar shows "Chat log" with the number of turns saved. The log stays on your computer. Nobody on the course staff sees it unless you turn it in, and it never includes your API key. To stop the log, delete logs/\_chatlog.json.

### 5\. Model gateway

Prove the key works. Open a terminal inside VS Code (menu Terminal, then New Terminal; it opens in your project folder) and run:  
curl.exe \-s \-H "Authorization: Bearer \<your key\>" https://llmproxy.cs.washington.edu/v1/models  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-10.png)  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## Linux

### 1\. Project folder

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P02/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week. It holds PROMPT.md, SCORECARD.md, an artifacts folder for the games the models write, and a logs folder for your chat log. Inside it, create a file named exactly .env: any text editor will do, or, once the folder is open in VS Code, right-click the folder name in the Explorer and choose New File. Paste these two lines into it:  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-11.png)  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. VS Code

Get the package for your distribution from [the VS Code download page](https://code.visualstudio.com/download) (.deb for Ubuntu). Install it. VS Code is installed when it opens to its welcome page.

### 3\. AI chat in VS Code

Install two extensions. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X. Search for LiteLLM and install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan. Then download the course extension, CSE 490 Course Tools, as cse490-tools.vsix from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix. Back in the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. That extension keeps the chat log described in step 4 and packages your turn-in.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-12.png)  
Point it at the course gateway. Open the Command Palette (Ctrl+Shift+P). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key. Switch agent mode off; this week the AI answers in chat and you save every file yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). Click the model picker at the bottom of the chat box; it reads Auto until you choose. Under CSE 490 you should see external/zai.glm-5, external/haiku-4-5-20251001 and internal/Qwen3.6-35B-A3B. Pick one before you send a message. If they are not listed, click "Manage Models...", then "Add Models", then "LiteLLM", choose the CSE 490 server, and tick the three. If any of them is still missing, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-13.png) ![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-14.png)

### 4\. Open the project

In VS Code, choose File, then Open Folder, and pick the starter folder. Save every game the models write into its artifacts folder, named the way artifacts/README.md says: the game name, one underscore, the model's short name, then .html. The course extension from step 3 sees logs/\_chatlog.json and, from then on, saves every chat you have with the course models in this folder to logs/\_chatlog.md, where you can read it any time. The status bar shows "Chat log" with the number of turns saved. The log stays on your computer. Nobody on the course staff sees it unless you turn it in, and it never includes your API key. To stop the log, delete logs/\_chatlog.json.

### 5\. Model gateway

Prove the key works. Open a terminal inside VS Code (menu Terminal, then New Terminal; it opens in your project folder) and run:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://llmproxy.cs.washington.edu/v1/models  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P02/images/setup-15.png)  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.
