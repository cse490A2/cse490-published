# Project 2 setup guide

This document provides instructions to set up your environment for CSE490's in-class projects, starting with Project 2\. 

1. Mac  
2. Windows  
3. Linux

## Mac

### 1\. Project folder

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P02/P02-starter.zip and unzip them. The unpacked folder, P02-starter, is your project folder for the week. It holds PROMPT.md, SCORECARD.md, an artifacts folder for the games the models write, and a logs folder for your chat log. Inside it, create a file named .env. Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://litellm-test.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. VS Code

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Open the downloaded file. Drag Visual Studio Code into Applications. Open it once so macOS trusts it, then check again.

### 3\. AI chat in VS Code

Install two extensions. In VS Code, open the Extensions panel: the four-squares icon on the left, or Cmd+Shift+X. Search for "LiteLLM VSCode Chat" by vivswan and click Install. Then download the course extension, CSE 490 Course Tools, as cse490-tools.vsix from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix. Back in the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. That extension keeps the chat log described in step 6 and packages your turn-in.  
Point it at the course gateway. Open the Command Palette (Cmd+Shift+P). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://litellm-test.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key. Switch agent mode off; this week the AI answers in chat and you save every file yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Cmd+I). The course's models do not appear in the model picker until you add them. Click the model picker at the bottom of the chat box, then "Manage Models...", then "Add Models", then "LiteLLM". Choose the CSE 490 server if it is offered. If it asks you for a server instead, give the base URL and your API key and keep every other answer at its default. Tick external/zai.glm-5, external/haiku-4-5-20251001, and internal/Qwen3.6-35B-A3B, then confirm. Those three now sit in the model picker; pick one before you send a message. If any of them is missing from the list, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 4\. Open the project

In VS Code, choose File, then Open Folder, and pick the P02-starter folder. Save every game the models write into its artifacts folder, named the way artifacts/README.md says: the game name, one underscore, the model's short name, then .html. The course extension from step 4 sees logs/\_chatlog.json and, from then on, saves every chat you have with the course models in this folder to logs/\_chatlog.md, where you can read it any time. The status bar shows "Chat log" with the number of turns saved. The log stays on your computer. Nobody on the course staff sees it unless you turn it in, and it never includes your API key. To stop the log, delete logs/\_chatlog.json.

### 5\. Model gateway

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## Windows

### 1\. Project folder

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P02/P02-starter.zip and unzip them. The unpacked folder, P02-starter, is your project folder for the week. It holds PROMPT.md, SCORECARD.md, an artifacts folder for the games the models write, and a logs folder for your chat log. Inside it, create a file named .env. Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://litellm-test.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. VS Code

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Run the installer. The defaults are fine. Then check again.

### 3\. AI chat in VS Code

Install two extensions. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X. Search for "LiteLLM VSCode Chat" by vivswan and click Install. Then download the course extension, CSE 490 Course Tools, as cse490-tools.vsix from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix. Back in the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. That extension keeps the chat log described in step 6 and packages your turn-in.  
Point it at the course gateway. Open the Command Palette (Ctrl+Shift+P). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://litellm-test.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key. Switch agent mode off; this week the AI answers in chat and you save every file yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). The course's models do not appear in the model picker until you add them. Click the model picker at the bottom of the chat box, then "Manage Models...", then "Add Models", then "LiteLLM". Choose the CSE 490 server if it is offered. If it asks you for a server instead, give the base URL and your API key and keep every other answer at its default. Tick external/zai.glm-5, external/haiku-4-5-20251001, and internal/Qwen3.6-35B-A3B, then confirm. Those three now sit in the model picker; pick one before you send a message. If any of them is missing from the list, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 4\. Open the project

In VS Code, choose File, then Open Folder, and pick the P02-starter folder. Save every game the models write into its artifacts folder, named the way artifacts/README.md says: the game name, one underscore, the model's short name, then .html. The course extension from step 4 sees logs/\_chatlog.json and, from then on, saves every chat you have with the course models in this folder to logs/\_chatlog.md, where you can read it any time. The status bar shows "Chat log" with the number of turns saved. The log stays on your computer. Nobody on the course staff sees it unless you turn it in, and it never includes your API key. To stop the log, delete logs/\_chatlog.json.

### 5\. Model gateway

Prove the key works. In PowerShell in your project folder:  
curl.exe \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## Linux

### 1\. Project folder

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P02/P02-starter.zip and unzip them. The unpacked folder, P02-starter, is your project folder for the week. It holds PROMPT.md, SCORECARD.md, an artifacts folder for the games the models write, and a logs folder for your chat log. Inside it, create a file named .env. Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://litellm-test.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. VS Code

Get the package for your distribution from [the VS Code download page](https://code.visualstudio.com/download) (.deb for Ubuntu). Install it, then check again.

### 3\. AI chat in VS Code

Install two extensions. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X. Search for "LiteLLM VSCode Chat" by vivswan and click Install. Then download the course extension, CSE 490 Course Tools, as cse490-tools.vsix from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix. Back in the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. That extension keeps the chat log described in step 6 and packages your turn-in.  
Point it at the course gateway. Open the Command Palette (Ctrl+Shift+P). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://litellm-test.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key. Switch agent mode off; this week the AI answers in chat and you save every file yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). The course's models do not appear in the model picker until you add them. Click the model picker at the bottom of the chat box, then "Manage Models...", then "Add Models", then "LiteLLM". Choose the CSE 490 server if it is offered. If it asks you for a server instead, give the base URL and your API key and keep every other answer at its default. Tick external/zai.glm-5, external/haiku-4-5-20251001, and internal/Qwen3.6-35B-A3B, then confirm. Those three now sit in the model picker; pick one before you send a message. If any of them is missing from the list, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 4\. Open the project

In VS Code, choose File, then Open Folder, and pick the P02-starter folder. Save every game the models write into its artifacts folder, named the way artifacts/README.md says: the game name, one underscore, the model's short name, then .html. The course extension from step 4 sees logs/\_chatlog.json and, from then on, saves every chat you have with the course models in this folder to logs/\_chatlog.md, where you can read it any time. The status bar shows "Chat log" with the number of turns saved. The log stays on your computer. Nobody on the course staff sees it unless you turn it in, and it never includes your API key. To stop the log, delete logs/\_chatlog.json.

### 5\. Model gateway

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.  
