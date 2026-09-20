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
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Cmd+I). The model picker at the bottom of the chat box shows qwen-3.6 alone at this point: the gateway lists the rest of your models only through the chat log, which step 7 sets up. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 5\. GitHub

Make a free GitHub account at [github.com](https://github.com) if you do not have one, and verify the email it sends you. Then, in VS Code, open the Accounts menu (the person icon at the bottom left) and sign in with GitHub. That is what lets Publish to GitHub work during the build.

### 6\. Project files

Inside your project folder, create two empty files: PROMPT.md and SCORECARD.md. Your game folders are created during the build.

### 7\. Chat log

On a yes, your chats with the course AI are saved to \_chatlog.md in this folder and turned in with it. Nothing else to do. In VS Code the chat's server is then named CSE 490 log, and its picker shows every model your key can use. On a no, you turn in a transcript yourself, and the picker keeps showing qwen-3.6 alone. The yes and the no are answers to the setup wizard; without the wizard there is no log.

### 8\. Model gateway

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

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

### 3\. VS Code

Download VS Code from [code.visualstudio.com](https://code.visualstudio.com). Run the installer. The defaults are fine. Then check again.

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
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). The model picker at the bottom of the chat box shows qwen-3.6 alone at this point: the gateway lists the rest of your models only through the chat log, which step 7 sets up. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 5\. GitHub

Make a free GitHub account at [github.com](https://github.com) if you do not have one, and verify the email it sends you. Then, in VS Code, open the Accounts menu (the person icon at the bottom left) and sign in with GitHub. That is what lets Publish to GitHub work during the build.

### 6\. Project files

Inside your project folder, create two empty files: PROMPT.md and SCORECARD.md. Your game folders are created during the build.

### 7\. Chat log

On a yes, your chats with the course AI are saved to \_chatlog.md in this folder and turned in with it. Nothing else to do. In VS Code the chat's server is then named CSE 490 log, and its picker shows every model your key can use. On a no, you turn in a transcript yourself, and the picker keeps showing qwen-3.6 alone. The yes and the no are answers to the setup wizard; without the wizard there is no log.

### 8\. Model gateway

Prove the key works. In PowerShell in your project folder:  
curl.exe \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.

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
Save the file. Open the chat panel (the speech-bubble icon at the top, or Ctrl+Alt+I). The model picker at the bottom of the chat box shows qwen-3.6 alone at this point: the gateway lists the rest of your models only through the chat log, which step 7 sets up. If the picker asks you to sign in to GitHub first, sign in; the course key still pays for every message.

### 5\. GitHub

Make a free GitHub account at [github.com](https://github.com) if you do not have one, and verify the email it sends you. Then, in VS Code, open the Accounts menu (the person icon at the bottom left) and sign in with GitHub. That is what lets Publish to GitHub work during the build.

### 6\. Project files

Inside your project folder, create two empty files: PROMPT.md and SCORECARD.md. Your game folders are created during the build.

### 7\. Chat log

On a yes, your chats with the course AI are saved to \_chatlog.md in this folder and turned in with it. Nothing else to do. In VS Code the chat's server is then named CSE 490 log, and its picker shows every model your key can use. On a no, you turn in a transcript yourself, and the picker keeps showing qwen-3.6 alone. The yes and the no are answers to the setup wizard; without the wizard there is no log.

### 8\. Model gateway

Prove the key works. In a terminal in your project folder:  
curl \-s \-H "Authorization: Bearer \<your key\>" https://litellm-test.cs.washington.edu/v1/models  
Replace \<your key\> with your API key. A working key returns a list of models. An "invalid key" error means a typo. No response at all means a network problem; if it keeps happening, tell the course staff.  
