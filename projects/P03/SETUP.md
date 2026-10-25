---
title: "P03 setup"
parent: "P03: The Agent Harness"
grand_parent: "Projects"
nav_order: 1
permalink: "/projects/P03/setup/"
---

# **Project 3 setup guide**

This document sets up your computer for CSE490’s in-class projects. There are two ways to do it, and they end in the same place. Pick one.

## **Option 1: the wizard (recommended)**

A small program that walks you through each step, with a picture of where to click, and checks each one on your computer. Download it once; every week it fetches that week’s project by itself. Requires Python 3.9+.  
Download [wizard-cse490.zip](https://github.com/cse490A2/cse490-published/releases/download/wizard/wizard-cse490.zip). It lands in your Downloads folder.

### **Mac**

Double-click the zip in Downloads to get the wizard folder. Then, in Terminal:  
`cd ~/Downloads/wizard`  
`python3 wizard.py`

### **Windows**

Right-click the zip in Downloads, choose "Extract All", open the wizard folder it makes, and double-click SETUP-WINDOWS.bat. If the blue "Windows protected your PC" box appears: "More info", then "Run anyway".

## **Option 2: by hand**

Read the section for your computer below (Mac, Windows or Linux) and do each step yourself. The steps are the same ones the wizard walks.

## **Mac**

### **1\. Course key**

Create a folder for the project. Inside it, create a file named .env.  
Inside, paste these two lines:  
`LITELLM_BASE_URL=https://llmproxy.cs.washington.edu`  
`LITELLM_API_KEY=<your key here>`  
Replace \<your key here\> with your given API key (it starts with sk).

### **2\. Python 3.9+**

Open [the Python download page](https://www.python.org/downloads/) and click the Download Python button.  
act: tap=button  
Open the downloaded file. Click Continue through the installer, then Install.

### **3\. VS Code**

Open [code.visualstudio.com](https://code.visualstudio.com) and click the Download button.  
act: tap=button  
Open the downloaded file. Drag Visual Studio Code into Applications.  
act: tap="Visual Studio Code"  
Open Visual Studio Code from Applications so macOS trusts it. VS Code is installed when it opens to its welcome page.

### **4\. AI chat in VS Code**

In VS Code, click the Extensions icon in the bar on the far left: four squares. Or press Cmd+Shift+X.  
act: tap=icon  
Search for LiteLLM. Install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan.  
act: type=search "LiteLLM" · tap=install  
   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-1.png)  
Open the Command Palette with Cmd+Shift+P. Run "Preferences: Open User Settings (JSON)".  
act: tap=palette  
Add this entry inside the outer braces:  
`"litellm-vscode-chat.servers": [`  
    `{`  
        `"label": "CSE 490",`  
        `"baseUrl": "https://llmproxy.cs.washington.edu",`  
        `"auth": { "apiKey": "<your key here>" }`  
    `}`  
`]`  
Replace \<your key here\> with your API key. Save the file.  
This week the AI answers in chat and you type every change yourself. Add this line beside the entry, with a comma between them, and save:  
`"chat.agent.enabled": false`  
Open the chat panel: the speech-bubble icon at the top, or Ctrl+Cmd+I. Click the model picker at the bottom of the chat box. It reads Auto until you choose, and the course models are not on its first screen: type the model's name in the search box at the top of the picker, haiku for example, and pick the entry marked CSE 490\. If nothing appears, click "Manage Models...", then "Add Models", then "LiteLLM", choose the CSE 490 server, and tick the models.  
   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-2.png)

### **5\. Course extension**

Download the course extension, cse490-tools.vsix, from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix (download it again if you installed it before October 21: version 0.5.4 or newer reads where VS Code 1.141 keeps your chats). In VS Code, open the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. It starts once your project files are in place; the chat log step covers that.

### **6\. Project files**

If your AGENTS.md says the student writes the harness themselves, or "Do not write harness.py for the student in one shot", it is the old starter's file: replace the whole file with the current one from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter/AGENTS.md (deleting one line is not enough), then start a new chat. Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week: harness.py, the untangle folder (the puzzle your agent solves in step 7: its rules, the graph, the judge and the viewer), the harness testbench and its files, systemprompt.md (the rules your harness reads, used in step 7 of the handout), and a logs folder for your chat log.  
Then give the project its own Python and the two packages the harness will import: `python3` \-m venv .venv (`py` \-3 on Windows), then .venv/bin/pip install requests python-dotenv (.venv\\Scripts\\pip on Windows), and pick that interpreter in VS Code with "Python: Select Interpreter".

### **7\. Chat log**

In VS Code, open your project folder itself (File, then Open Folder, then p03), not the folder above it: the Explorer's top entry must read P03. Then restart VS Code's extensions (the "Restart Extensions" button at the top of the Extensions panel, or "Developer: Reload Window" from the Command Palette). The status bar reads "Chat log: 0 turns" when the extension is running; every chat with the course models is then saved to logs/\_chatlog.md in your project folder.

### **8\. Model gateway**

Prove the key works. In a terminal in your project folder:  
`curl -s -H "Authorization: Bearer <your key>" https://llmproxy.cs.washington.edu/v1/models`  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## **Windows**

### **1\. Course key**

Create a folder for the project. Inside it, create a file named .env.  
Inside, paste these two lines:  
`LITELLM_BASE_URL=https://llmproxy.cs.washington.edu`  
`LITELLM_API_KEY=<your key here>`  
Replace \<your key here\> with your given API key (it starts with sk).

### **2\. Python 3.9+**

Open [the Python download page](https://www.python.org/downloads/) and click the Download Python button.  
act: tap=button  
Open the downloaded file. Check the "Add python.exe to PATH" box at the bottom, then click Install Now.

### **3\. VS Code**

Open [code.visualstudio.com](https://code.visualstudio.com) and click the Download button.  
act: tap=button  
Open the downloaded file. The defaults are fine.  
Open Visual Studio Code from the Start menu. VS Code is installed when it opens to its welcome page.

### **4\. AI chat in VS Code**

In VS Code, click the Extensions icon in the bar on the far left: four squares. Or press Ctrl+Shift+X.  
act: tap=icon  
Search for LiteLLM. Install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan.  
act: type=search "LiteLLM" · tap=install  
   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-1.png)  
Open the Command Palette with Ctrl+Shift+P. Run "Preferences: Open User Settings (JSON)".  
act: tap=palette  
Add this entry inside the outer braces:  
`"litellm-vscode-chat.servers": [`  
    `{`  
        `"label": "CSE 490",`  
        `"baseUrl": "https://llmproxy.cs.washington.edu",`  
        `"auth": { "apiKey": "<your key here>" }`  
    `}`  
`]`  
Replace \<your key here\> with your API key. Save the file.  
This week the AI answers in chat and you type every change yourself. Add this line beside the entry, with a comma between them, and save:  
`"chat.agent.enabled": false`  
Open the chat panel: the speech-bubble icon at the top, or Ctrl+Alt+I. Click the model picker at the bottom of the chat box. It reads Auto until you choose, and the course models are not on its first screen: type the model's name in the search box at the top of the picker, haiku for example, and pick the entry marked CSE 490\. If nothing appears, click "Manage Models...", then "Add Models", then "LiteLLM", choose the CSE 490 server, and tick the models.  
   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-2.png)

### **5\. Course extension**

Download the course extension, cse490-tools.vsix, from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix (download it again if you installed it before October 21: version 0.5.4 or newer reads where VS Code 1.141 keeps your chats). In VS Code, open the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. It starts once your project files are in place; the chat log step covers that.

### **6\. Project files**

If your AGENTS.md says the student writes the harness themselves, or "Do not write harness.py for the student in one shot", it is the old starter's file: replace the whole file with the current one from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter/AGENTS.md (deleting one line is not enough), then start a new chat. Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week: harness.py, the untangle folder (the puzzle your agent solves in step 7: its rules, the graph, the judge and the viewer), the harness testbench and its files, systemprompt.md (the rules your harness reads, used in step 7 of the handout), and a logs folder for your chat log.  
Then give the project its own Python and the two packages the harness will import: `python3` \-m venv .venv (`py` \-3 on Windows), then .venv/bin/pip install requests python-dotenv (.venv\\Scripts\\pip on Windows), and pick that interpreter in VS Code with "Python: Select Interpreter".

### **7\. Chat log**

In VS Code, open your project folder itself (File, then Open Folder, then p03), not the folder above it: the Explorer's top entry must read P03. Then restart VS Code's extensions (the "Restart Extensions" button at the top of the Extensions panel, or "Developer: Reload Window" from the Command Palette). The status bar reads "Chat log: 0 turns" when the extension is running; every chat with the course models is then saved to logs/\_chatlog.md in your project folder.

### **8\. Model gateway**

Prove the key works. In PowerShell in your project folder:  
`curl.exe -s -H "Authorization: Bearer <your key>" https://llmproxy.cs.washington.edu/v1/models`  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## **Linux**

### **1\. Course key**

Create a folder for the project. Inside it, create a file named .env.  
Inside, paste these two lines:  
`LITELLM_BASE_URL=https://llmproxy.cs.washington.edu`  
`LITELLM_API_KEY=<your key here>`  
Replace \<your key here\> with your given API key (it starts with sk).

### **2\. Python 3.9+**

On Debian or Ubuntu, run this in a terminal:  
`sudo apt install python3`

### **3\. VS Code**

Open [the VS Code download page](https://code.visualstudio.com/download). Get the package for your distribution: .deb for Ubuntu.  
act: tap=button  
Install the package you downloaded. On Ubuntu, open it, or run apt on it in a terminal.  
act: tap=code\_amd64.deb  
Open Visual Studio Code. It is installed when it opens to its welcome page.

### **4\. AI chat in VS Code**

In VS Code, click the Extensions icon in the bar on the far left: four squares. Or press Ctrl+Shift+X.  
act: tap=icon  
Search for LiteLLM. Install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan.  
act: type=search "LiteLLM" · tap=install  
   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-1.png)  
Open the Command Palette with Ctrl+Shift+P. Run "Preferences: Open User Settings (JSON)".  
act: tap=palette  
Add this entry inside the outer braces:  
`"litellm-vscode-chat.servers": [`  
    `{`  
        `"label": "CSE 490",`  
        `"baseUrl": "https://llmproxy.cs.washington.edu",`  
        `"auth": { "apiKey": "<your key here>" }`  
    `}`  
`]`  
Replace \<your key here\> with your API key. Save the file.  
This week the AI answers in chat and you type every change yourself. Add this line beside the entry, with a comma between them, and save:  
`"chat.agent.enabled": false`  
Open the chat panel: the speech-bubble icon at the top, or Ctrl+Alt+I. Click the model picker at the bottom of the chat box. It reads Auto until you choose, and the course models are not on its first screen: type the model's name in the search box at the top of the picker, haiku for example, and pick the entry marked CSE 490\. If nothing appears, click "Manage Models...", then "Add Models", then "LiteLLM", choose the CSE 490 server, and tick the models.  
   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-2.png)

### **5\. Course extension**

Download the course extension, cse490-tools.vsix, from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix (download it again if you installed it before October 21: version 0.5.4 or newer reads where VS Code 1.141 keeps your chats). In VS Code, open the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file. It starts once your project files are in place; the chat log step covers that.

### **6\. Project files**

If your AGENTS.md says the student writes the harness themselves, or "Do not write harness.py for the student in one shot", it is the old starter's file: replace the whole file with the current one from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter/AGENTS.md (deleting one line is not enough), then start a new chat. Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week: harness.py, the untangle folder (the puzzle your agent solves in step 7: its rules, the graph, the judge and the viewer), the harness testbench and its files, systemprompt.md (the rules your harness reads, used in step 7 of the handout), and a logs folder for your chat log.  
Then give the project its own Python and the two packages the harness will import: `python3` \-m venv .venv (`py` \-3 on Windows), then .venv/bin/pip install requests python-dotenv (.venv\\Scripts\\pip on Windows), and pick that interpreter in VS Code with "Python: Select Interpreter".

### **7\. Chat log**

In VS Code, open your project folder itself (File, then Open Folder, then p03), not the folder above it: the Explorer's top entry must read P03. Then restart VS Code's extensions (the "Restart Extensions" button at the top of the Extensions panel, or "Developer: Reload Window" from the Command Palette). The status bar reads "Chat log: 0 turns" when the extension is running; every chat with the course models is then saved to logs/\_chatlog.md in your project folder.

### **8\. Model gateway**

Prove the key works. In a terminal in your project folder:  
`curl -s -H "Authorization: Bearer <your key>" https://llmproxy.cs.washington.edu/v1/models`  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.
