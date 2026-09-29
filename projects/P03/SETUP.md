---
title: "P03 setup"
parent: "P03: The Agent Harness"
grand_parent: "Projects"
nav_order: 1
permalink: "/projects/P03/setup/"
---

# **Project 3 setup guide**

This document provides instructions to set up your environment for CSE490’s in-class projects. If you would like to follow an interactive guide instead, try out [the wizard](https://canvas.uw.edu/courses/1916846/pages/course-setup-the-wizard).

## **Downloading the Wizard**

Requires Python 3.9+  
Download the Wizard, currently found in the Drive folder.

### **Mac**

Double-click the zip in Downloads to get the wizard folder. Then, in Terminal:  
cd \~/Downloads/wizard  
python3 wizard.py

### **Windows**

Right-click the zip in Downloads, choose "Extract All", open the wizard folder it makes, and double-click SETUP-WINDOWS.bat. If the blue "Windows protected your PC" box appears: "More info", then "Run anyway".

## **Mac**

### **1\. Course key**

Create a folder for the project. Inside it, create a file named .env.  
Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### **2\. Python 3.9+**

Install the current Python from [the Python download page](https://python.org/downloads). Run the installer. Then check again from a fresh terminal window.

### **3\. VS Code**

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Open the downloaded file. Drag Visual Studio Code into Applications. Open it once so macOS trusts it, then check again.

### **4\. AI chat in VS Code**

Install the extension. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X (Cmd+Shift+X on a Mac). Search for "LiteLLM VSCode Chat" by vivswan and click Install.  
Point it at the course gateway. Open the Command Palette (Ctrl+Shift+P; Cmd+Shift+P on a Mac). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key.  
Switch agent mode off – this week the AI answers in chat and you type every change yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file, then check again.

### **5\. Course extension**

Download the course extension, cse490-tools.vsix, from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix In VS Code, open the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file.

### **6\. Project files**

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week: harness.py, hello\_world.py, the harness testbench and its files, and a logs folder for your chat log.

### **7\. Model gateway**

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://llmproxy.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## **Windows**

### **1\. Course key**

Create a folder for the project. Inside it, create a file named .env.  
Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### **2\. Python 3.9+**

Install the current Python from [the Python download page](https://python.org/downloads). In the installer, check the "Add python.exe to PATH" box. Then check again from a fresh terminal window.

### **3\. VS Code**

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Run the installer. The defaults are fine. Then check again.

### **4\. AI chat in VS Code**

Install the extension. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X (Cmd+Shift+X on a Mac). Search for "LiteLLM VSCode Chat" by vivswan and click Install.  
Point it at the course gateway. Open the Command Palette (Ctrl+Shift+P; Cmd+Shift+P on a Mac). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key.  
Switch agent mode off – this week the AI answers in chat and you type every change yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file, then check again.

### **5\. Course extension**

Download the course extension, cse490-tools.vsix, from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix In VS Code, open the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file.

### **6\. Project files**

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week: harness.py, hello\_world.py, the harness testbench and its files, and a logs folder for your chat log.

### **7\. Model gateway**

Prove the key works. In PowerShell in your project folder:  
curl.exe \-s \-H "Authorization: Bearer \<your key\>" https://llmproxy.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

## **Linux**

### **1\. Course key**

Create a folder for the project. Inside it, create a file named .env.  
Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### **2\. Python 3.9+**

On Debian or Ubuntu: sudo apt install python3. Then check again.

### **3\. VS Code**

Get the package for your distribution from [the VS Code download page](https://code.visualstudio.com/download) (.deb for Ubuntu). Install it, then check again.

### **4\. AI chat in VS Code**

Install the extension. In VS Code, open the Extensions panel: the four-squares icon on the left, or Ctrl+Shift+X (Cmd+Shift+X on a Mac). Search for "LiteLLM VSCode Chat" by vivswan and click Install.  
Point it at the course gateway. Open the Command Palette (Ctrl+Shift+P; Cmd+Shift+P on a Mac). Run "Preferences: Open User Settings (JSON)". Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your given API key.  
Switch agent mode off – this week the AI answers in chat and you type every change yourself. Add this line beside the entry above:  
"chat.agent.enabled": false  
Save the file, then check again.

### **5\. Course extension**

Download the course extension, cse490-tools.vsix, from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix In VS Code, open the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file.

### **6\. Project files**

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week: harness.py, hello\_world.py, the harness testbench and its files, and a logs folder for your chat log.

### **7\. Model gateway**

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://llmproxy.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.