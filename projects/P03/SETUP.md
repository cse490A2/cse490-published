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
cd \~/Downloads/wizard  
python3 wizard.py

### **Windows**

Right-click the zip in Downloads, choose "Extract All", open the wizard folder it makes, and double-click SETUP-WINDOWS.bat. If the blue "Windows protected your PC" box appears: "More info", then "Run anyway".

## **Option 2: by hand**

Read the section for your computer below (Mac, Windows or Linux) and do each step yourself. The steps are the same ones the wizard walks.

## **Mac**

### **1\. Course key**

Create a folder for the project. Inside it, create a file named .env.  
Inside, paste these two lines:  
LITELLM\_BASE\_URL=https://llmproxy.cs.washington.edu  
LITELLM\_API\_KEY=\<your key here\>  
Replace \<your key here\> with your given API key (it starts with sk).

### **2\. Python 3.9+**

Open [the Python download page](https://www.python.org/downloads/) and click the Download Python button.  
Open the downloaded file. Click Continue through the installer, then Install.

### **3\. VS Code**

Open [code.visualstudio.com](https://code.visualstudio.com) and click the Download button.  
Open the downloaded file. Drag Visual Studio Code into Applications.  
Open Visual Studio Code from Applications so macOS trusts it. VS Code is installed when it opens to its welcome page.

### **4\. AI chat in VS Code**

In VS Code, click the Extensions icon in the bar on the far left: four squares. Or press Cmd+Shift+X.  
Search for LiteLLM. Install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-1.png)  
Open the Command Palette with Cmd+Shift+P. Run "Preferences: Open User Settings (JSON)".  
Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your API key. Save the file.  
This week the AI answers in chat and you type every change yourself. Add this line beside the entry, with a comma between them, and save:  
"chat.agent.enabled": false  
Open the chat panel: the speech-bubble icon at the top, or Ctrl+Cmd+I. Click the model picker at the bottom of the chat box. It reads Auto until you choose. Pick a model under CSE 490\.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-2.png)

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

Open [the Python download page](https://www.python.org/downloads/) and click the Download Python button.  
Open the downloaded file. Check the "Add python.exe to PATH" box at the bottom, then click Install Now.

### **3\. VS Code**

Open [code.visualstudio.com](https://code.visualstudio.com) and click the Download button.  
Open the downloaded file. The defaults are fine.  
Open Visual Studio Code from the Start menu. VS Code is installed when it opens to its welcome page.

### **4\. AI chat in VS Code**

In VS Code, click the Extensions icon in the bar on the far left: four squares. Or press Ctrl+Shift+X.  
Search for LiteLLM. Install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-1.png)  
Open the Command Palette with Ctrl+Shift+P. Run "Preferences: Open User Settings (JSON)".  
Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your API key. Save the file.  
This week the AI answers in chat and you type every change yourself. Add this line beside the entry, with a comma between them, and save:  
"chat.agent.enabled": false  
Open the chat panel: the speech-bubble icon at the top, or Ctrl+Alt+I. Click the model picker at the bottom of the chat box. It reads Auto until you choose. Pick a model under CSE 490\.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-2.png)

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

On Debian or Ubuntu, run this in a terminal:  
sudo apt install python3

### **3\. VS Code**

Open [the VS Code download page](https://code.visualstudio.com/download). Get the package for your distribution: .deb for Ubuntu.  
Install the package you downloaded. On Ubuntu, open it, or run apt on it in a terminal.  
Open Visual Studio Code. It is installed when it opens to its welcome page.

### **4\. AI chat in VS Code**

In VS Code, click the Extensions icon in the bar on the far left: four squares. Or press Ctrl+Shift+X.  
Search for LiteLLM. Install "LiteLLM Provider for GitHub Copilot Chat" by Vivswan.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-1.png)  
Open the Command Palette with Ctrl+Shift+P. Run "Preferences: Open User Settings (JSON)".  
Add this entry inside the outer braces:  
"litellm-vscode-chat.servers": \[  
    {  
        "label": "CSE 490",  
        "baseUrl": "https://llmproxy.cs.washington.edu",  
        "auth": { "apiKey": "\<your key here\>" }  
    }  
\]  
Replace \<your key here\> with your API key. Save the file.  
This week the AI answers in chat and you type every change yourself. Add this line beside the entry, with a comma between them, and save:  
"chat.agent.enabled": false  
Open the chat panel: the speech-bubble icon at the top, or Ctrl+Alt+I. Click the model picker at the bottom of the chat box. It reads Auto until you choose. Pick a model under CSE 490\.  
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P03/images/setup-2.png)

### **5\. Course extension**

Download the course extension, cse490-tools.vsix, from https://github.com/cse490A2/cse490-published/releases/latest/download/cse490-tools.vsix In VS Code, open the Extensions panel, open the three-dots menu at the top, choose "Install from VSIX...", and pick the downloaded file.

### **6\. Project files**

Download the starter files from https://github.com/cse490A2/cse490-published/raw/main/projects/P03/starter.zip and unzip them. The unpacked folder, starter, is your project folder for the week: harness.py, hello\_world.py, the harness testbench and its files, and a logs folder for your chat log.

### **7\. Model gateway**

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://llmproxy.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.
