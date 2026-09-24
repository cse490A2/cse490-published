# Project 2 setup guide

This document provides instructions to set up your environment for CSE490's in-class projects, starting with Project 2\. 

1. Mac  
2. Windows  
3. Linux

## Mac

### 1\. Course key

Create a folder for the project. Inside it, create a file named .env. Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://litellm-test.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. git

Open the Terminal app and type:  
git \--version  
macOS will offer to install the developer tools. Accept, wait for it to finish, then check again. Then tell git who you are, once, with your name and the email you will use for GitHub:  
git config \--global user.name "Your Name"  
git config \--global user.email "you@example.com"

### 3\. VS Code

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Open the downloaded file. Drag Visual Studio Code into Applications. Open it once so macOS trusts it, then check again.

### 4\. AI chat in VS Code

Install the extension. In VS Code, open the Extensions panel: the four-squares icon on the left, or Cmd+Shift+X. Search for "LiteLLM VSCode Chat" by vivswan and click Install.  
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
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Cmd+I). The course's models do not appear in the model picker until you add them. Click the model picker at the bottom of the chat box, then "Manage Models...", then "Add Models", then "LiteLLM". Choose the CSE 490 server if it is offered. If it asks you for a server instead, give the base URL and your API key and keep every other answer at its default. Tick external/haiku-4-5-20251001, external/kimi-k3, and external/deepseek.v3.2, then confirm. Those three now sit in the model picker; pick one before you send a message. If any of them is missing from the list, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 5\. GitHub

Make a free GitHub account at [github.com](https://github.com) if you do not have one, and verify the email it sends you. Then, in VS Code, open the Accounts menu (the person icon at the bottom left) and sign in with GitHub. VS Code's chat may ask you to sign in, and projects from week 3 on keep their code on GitHub.

### 6\. Project files

Download the [starter files](https://github.com/cse490A2/cse490-published/raw/main/projects/P02/P02-starter.zip) and unzip them into your project folder: PROMPT.md, SCORECARD.md, and a chat log. You save your game files here during the build. Open the folder in VS Code. When it asks whether to allow automatic tasks in this folder, click Allow; that switches the chat log on. From then on, every chat you have with the course models in this folder is saved to \_chatlog.md, next to your other files, where you can read it any time. The log stays on your computer. Nobody on the course staff sees it unless you upload it yourself, and it never includes your API key. To stop the log, delete \_chatlog.py from the folder.

### 7\. Model gateway

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## Windows

### 1\. Course key

Create a folder for the project. Inside it, create a file named .env. Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://litellm-test.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. git

Download and install git from [git-scm.com](https://git-scm.com/downloads). The default options are all fine. Then, from a fresh terminal window, tell git who you are, once:  
git config \--global user.name "Your Name"  
git config \--global user.email "you@example.com"

### 3\. Python

Download Python from [python.org/downloads](https://www.python.org/downloads/) and run the installer. Tick "Add python.exe to PATH", then choose Install Now. Then, from a fresh PowerShell window, check it:  
py \--version  
A version number means it worked. The chat log in step 7 runs on Python.

### 4\. VS Code

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Run the installer. The defaults are fine. Then check again.

### 5\. AI chat in VS Code

Install the extension. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X. Search for "LiteLLM VSCode Chat" by vivswan and click Install.  
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
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). The course's models do not appear in the model picker until you add them. Click the model picker at the bottom of the chat box, then "Manage Models...", then "Add Models", then "LiteLLM". Choose the CSE 490 server if it is offered. If it asks you for a server instead, give the base URL and your API key and keep every other answer at its default. Tick external/haiku-4-5-20251001, external/kimi-k3, and external/deepseek.v3.2, then confirm. Those three now sit in the model picker; pick one before you send a message. If any of them is missing from the list, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 6\. GitHub

Make a free GitHub account at [github.com](https://github.com) if you do not have one, and verify the email it sends you. Then, in VS Code, open the Accounts menu (the person icon at the bottom left) and sign in with GitHub. VS Code's chat may ask you to sign in, and projects from week 3 on keep their code on GitHub.

### 7\. Project files

Download the [starter files](https://github.com/cse490A2/cse490-published/raw/main/projects/P02/P02-starter.zip) and unzip them into your project folder: PROMPT.md, SCORECARD.md, and a chat log. You save your game files here during the build. Open the folder in VS Code. When it asks whether to allow automatic tasks in this folder, click Allow; that switches the chat log on. From then on, every chat you have with the course models in this folder is saved to \_chatlog.md, next to your other files, where you can read it any time. The log stays on your computer. Nobody on the course staff sees it unless you upload it yourself, and it never includes your API key. To stop the log, delete \_chatlog.py from the folder.

### 8\. Model gateway

Prove the key works. In PowerShell in your project folder:  
curl.exe \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## Linux

### 1\. Course key

Create a folder for the project. Inside it, create a file named .env. Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://litellm-test.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### 2\. git

On Debian or Ubuntu:  
sudo apt install git  
Then tell git who you are, once:  
git config \--global user.name "Your Name"  
git config \--global user.email "you@example.com"

### 3\. VS Code

Get the package for your distribution from [the VS Code download page](https://code.visualstudio.com/download) (.deb for Ubuntu). Install it, then check again.

### 4\. AI chat in VS Code

Install the extension. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X. Search for "LiteLLM VSCode Chat" by vivswan and click Install.  
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
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). The course's models do not appear in the model picker until you add them. Click the model picker at the bottom of the chat box, then "Manage Models...", then "Add Models", then "LiteLLM". Choose the CSE 490 server if it is offered. If it asks you for a server instead, give the base URL and your API key and keep every other answer at its default. Tick external/haiku-4-5-20251001, external/kimi-k3, and external/deepseek.v3.2, then confirm. Those three now sit in the model picker; pick one before you send a message. If any of them is missing from the list, tell the course staff. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 5\. GitHub

Make a free GitHub account at [github.com](https://github.com) if you do not have one, and verify the email it sends you. Then, in VS Code, open the Accounts menu (the person icon at the bottom left) and sign in with GitHub. VS Code's chat may ask you to sign in, and projects from week 3 on keep their code on GitHub.

### 6\. Project files

Download the [starter files](https://github.com/cse490A2/cse490-published/raw/main/projects/P02/P02-starter.zip) and unzip them into your project folder: PROMPT.md, SCORECARD.md, and a chat log. You save your game files here during the build. Open the folder in VS Code. When it asks whether to allow automatic tasks in this folder, click Allow; that switches the chat log on. From then on, every chat you have with the course models in this folder is saved to \_chatlog.md, next to your other files, where you can read it any time. The log stays on your computer. Nobody on the course staff sees it unless you upload it yourself, and it never includes your API key. To stop the log, delete \_chatlog.py from the folder.

### 7\. Model gateway

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models that includes the three course models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.  
