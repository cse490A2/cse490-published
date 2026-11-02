---
title: "P06 setup"
parent: "P06"
grand_parent: "Projects"
nav_order: 1
permalink: "/projects/P06/setup/"
---

# **Project 6 setup guide**

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

### **Part A: mark for attendance (in class)**

#### **Mark for attendance**

Your in-person attendance is worth 2 points of your assignment grade. There are two ways to mark attendance, both using the Wizard:

##### **A. Wizard TUI**

> 1. In your Terminal:  
>    `python3 wizard.py`  
> 2. Choose Attendance

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-1.png)

> 3. Type in the attendance code, then press enter

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-2.png)

> 4. Confirmation message

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-3.png)

##### **B. Wizard CLI**

`python3 wizard.py attendance <code>`

### **Part 1: your harness, your repository and the code (every student)**

#### **1\. Your Project 5 harness**

**What it is for.** Your harness is the agent you built in Projects 3 to 5: harness.py, systemprompt.md (its system prompt) and the skills folder. In Project 5 it ran inside your codespace. Project 6 runs on your laptop, in a folder of its own named p06, because the code you fix and the tests you run live there too. This step brings the harness down and gives it its keys.  
**How it works.** The codespace is a computer in the cloud; `gh codespace cp` copies files between it and your laptop over the same connection VS Code uses. Your codespace's name is on github.com/codespaces. In the codespace the harness read its model's address and key from two environment variables the codespace set, PURPLE\_BASE\_URL and PURPLE\_API\_KEY. On your laptop nothing sets them, so they go in the file `.env` beside harness.py, and the harness has to read that file.  
**Do this.**

> 1. On your laptop, make a folder named p06 and open a Terminal in it.  
> 2. Find your codespace's name at https://github.com/codespaces. It looks like orange-yodel-576g7xq5rpj344r: two words and a code. `gh codespace list` prints it; if there are several, pick the one you used last (the most recent in `gh codespace list`).  
> 3. Run, with that name in place of \<codespace\>:  
>    `gh codespace cp -e -r -c <codespace> remote:/workspaces/cse490-p05-starter/harness .`

A folder named harness appears in p06 with harness.py, systemprompt.md and the skills folder inside it: move everything inside it up into p06, so harness.py sits beside .env. RULES.md may come along from Project 5; step 4 replaces it with settings.json, so leave it alone until the handout says to delete it.

> 4. Make a file named `.env` in p06 with these lines, your Purple key from purple.uw.edu (Project 5's step 4\) in place of \<your Purple key\>:  
>    `PURPLE_BASE_URL=https://apim-n1ai-usw2-065882797.azure-api.net/openai/v1`  
>    `PURPLE_API_KEY=<your Purple key>`

If your harness.py reads the address and key under other names, use those names.

> 5. Give your harness its own Python environment in p06, with a Python of 3.10 or newer (the Mac's built-in `python3` is 3.9 and cannot install mcp, and a Homebrew Python refuses to install into itself): `python3.12 -m venv .venv-harness && .venv-harness/bin/pip install python-dotenv mcp requests` (any newer Python in place of 3.12). From here on, run the harness with that environment's Python: .venv-harness/bin/python harness.py.  
> 6. If your harness reads only the environment and not `.env`, ask the LiteLLM chat in VS Code: "Read harness.py. At startup, load the variables in `.env` beside it into the environment when they are not set already. Change nothing else." Read the change before you accept it.

**Common problems.**

> * *gh says there is no codespace.* Start it once from github.com/codespaces, then run the copy again; a stopped codespace cannot be copied from.  
> * *The copy prints nothing for minutes.* A stopped codespace is starting; wait, or press Ctrl+C and run the copy again. If it fails twice, download the files from the codespace's Explorer instead.  
> * *A folder named harness appeared inside p06.* Move everything inside it up into p06, so harness.py sits beside .env.  
> * *I do not have the GitHub command line.* Install gh from cli.github.com and run `gh auth login`, or download harness.py, systemprompt.md and the skills folder from the codespace's Explorer (right-click, Download) into p06.  
> * *I lost my Purple key.* On purple.uw.edu open Settings, API Projects, your CSE490-P05 project: the Primary Key is there.  
> * *The harness answers with a 401\.* The key in `.env` is wrong or has a stray space. Copy it again.

#### **2\. Your repository**

**What it is for.** Project 6 happens in a repository of your own on GitHub: a private copy of thumbor, the image server, named p06-\<your login\> under your own account. It carries the five issues on the menu, and the handout has you fix three of them. It is thumbor as it was in September 2026, with its full history, before four of the five bugs were fixed in the real project; the fifth is a feature that does not exist yet. Your harness pushes branches and opens pull requests there, and the course grader reads it. Nothing is created in the course organisation, so nobody has to approve anything.  
**How it works.** The course starter, cse490A2/cse490-p06-starter, is a public template repository. GitHub can copy a template into a new repository under your account in one command, then it copies the files in the background for a minute. A copy made from a template has no link back to the starter, so a pull request you open stays in your repository. It also keeps none of thumbor's history, so the wizard pushes the starter's full history over the copy, and git blame and git log work the way the lecture shows. The five issues are not part of a template copy either, so the wizard files them from the starter's course/issues.json. Under each of the four real ones it posts the conversation from thumbor's own report, so you and your harness can read what the reporter and the maintainers said. It invites the course grader to read the repository so your pull requests can be graded.  
**Do this.**

> 1. Install the GitHub command line, gh, from cli.github.com if you do not have it (`brew install gh`), and git from git-scm.com if `git --version` does not answer. In your Terminal run `gh auth login`: pick GitHub.com, HTTPS, and sign in with a web browser. That account is the one the repository is made under.  
> 2. In the wizard, pick Project 6, open the step "Your repository" and choose "Create the repository now". It makes p06-\<your login\> from the template, waits for the copy, pushes thumbor's history, files the five issues with their conversations and invites the grader, printing each step. The history push takes about a minute.  
> 3. Without the wizard, you still need the wizard folder for its script: download https://github.com/cse490A2/cse490-published/releases/download/wizard/wizard-cse490.zip once and unpack it, the same zip Option 1 uses. In your p06 folder run, with your GitHub login in place of \<your login\>:  
>    `gh repo create p06-<your login> --private --template cse490A2/cse490-p06-starter`

then, once https://github.com/\<your login\>/p06-\<your login\> shows the code, run the wizard's script to push the history, file the issues and invite the grader:  
`python3 ~/Downloads/wizard/packs/p06/10-repo/make_repo.py`  
(the p06 pack is in the wizard folder once the wizard has run with Project 6 open; \<wizard folder\> is wherever you unpacked it)

> 4. Open https://github.com/\<your login\>/p06-\<your login\>/issues in the browser: five issues, each labelled menu, four of them with comments copied from the thumbor project.

**Common problems.**

> * *gh repo create says the name already exists.* Fine: go on to the wizard's script, which adds only what is missing.  
> * *gh is signed in as someone else.* The repository is made under the signed-in account. Run `gh auth login` again as the account you want.  
> * *The repository is there but empty.* GitHub is still copying the template. Wait a minute and look again.  
> * *A repository named p06-\<your login\> already exists under my account.* The script leaves it alone and only adds what is missing: the history, the issues, their conversations, the grader.  
> * *The wizard says the repository has no history.* git was not installed when the repository was made. Install git, then pick "Create the repository now" again.  
> * *GitHub asked the course staff to approve a token.* You made the token with the course organisation as its owner. That is the next step's mistake, not this one's: the owner is your own account.

#### **3\. GitHub token**

**What it is for.** Your harness needs its own key to your repository: a fine-grained personal access token, made on github.com, that can reach p06-\<your login\> and nothing else. The GitHub MCP server (step 4\) sends it with every request, the way your course key goes to the gateway. GitHub has no command for making one, so you make it in the browser; the wizard tests what it can reach.  
**How it works.** A fine-grained token is tied to one owner and a list of repositories, with a permission per kind of thing. Its owner is the account that holds the repository: your own account (step 2), not the course organisation. A token owned by an organisation needs an administrator's approval; one owned by you needs nobody's. The token is shown once, when it is made, and goes in `.env` beside your harness as GITHUB\_PERSONAL\_ACCESS\_TOKEN. The wizard asks GitHub three questions with it: can it read your repository, can it write to it, can it see any other repository. The answers must be yes, yes, no.  
**Do this.**

> 1. On github.com, click your profile picture, then Settings, Developer settings, Personal access tokens, Fine-grained tokens, Generate new token. Or open https://github.com/settings/personal-access-tokens/new.  
> 2. Token name: cse490-p06. Expiration: 90 days. Resource owner: your own account, not the course organisation.  
> 3. Under Repository access choose "Only select repositories" and pick p06-\<your login\>. One repository, no more.  
> 4. Under Repository permissions set Contents to Read and write, Issues to Read and write, and Pull requests to Read and write. Metadata becomes Read on its own. Leave everything else at No access.  
> 5. Click Generate token. GitHub shows it once, a long string starting with github\_pat\_. Copy the whole thing now.  
> 6. Open `.env` in your p06 folder (step 1\) and add this line, your token in place of \<your token\>, then save:  
>    `GITHUB_PERSONAL_ACCESS_TOKEN=<your token>`

**Common problems.**

> * *I used `gh auth token` instead.* That is a different kind of token: it reaches every repository you have, so the wizard's third check fails. Make the fine-grained one above; it starts with github\_pat\_.  
> * *The wizard says the token sees other repositories.* "All repositories" was chosen, or more than one was picked. Delete that token on github.com and make a new one with only p06-\<your login\>.  
> * *The wizard says the token cannot write.* Contents was left at Read. Edit the token on github.com: Contents, Issues and Pull requests to Read and write.  
> * *GitHub says the token is unknown (401).* A character was lost when pasting, or the token was deleted. Paste it again whole, or make a new one.  
> * *I closed the page before copying.* The token cannot be shown again. Delete it and make another.  
> * *The resource owner list shows cse490A2.* Pick your own account anyway. The repository is yours.

#### **4\. GitHub MCP server**

**What it is for.** The GitHub MCP server is the program that gives your harness GitHub's tools: read an issue, open a pull request, read its diff, post a review. It is the same kind of server as Blender's in Project 5, and your harness connects to it the same way, over a pipe, from an entry in settings.json.  
**How it works.** The server is one file, github-mcp-server, released by GitHub; the course pins release 2.0.2. Your harness starts it with the command `github-mcp-server stdio` and talks to it over standard input and output. The server reads your token (step 3\) from the environment variable GITHUB\_PERSONAL\_ACCESS\_TOKEN, which your harness passes it from .env. settings.json names the server, so the harness knows to start it; it is the same file shape Claude Code and Codex read, with the servers under mcpServers and the git commands and GitHub tools the harness must refuse under permissions. Project 5's RULES.md did this job as prose; in the handout's step 3 your harness switches to settings.json and RULES.md goes away.  
**Do this.**

> 1. Download github-mcp-server\_Darwin\_arm64.tar.gz (Apple silicon) or github-mcp-server\_Darwin\_x86\_64.tar.gz (Intel) from https://github.com/github/github-mcp-server/releases/tag/v2.0.2.  
> 2. Double-click it to unpack. Move the file github-mcp-server into your p06 folder (step 1), beside harness.py.  
> 3. Check it in your Terminal, in p06: `./github-mcp-server --version` prints Version: 2.0.2 among its lines.  
> 4. Make a file named settings.json in p06, beside harness.py, with this in it:  
>    `{`  
>      `"mcpServers": {`  
>        `"github": {`  
>          `"command": "./github-mcp-server",`  
>          `"args": ["stdio"],`  
>          `"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"}`  
>        `}`  
>      `},`  
>      `"permissions": {`  
>        `"deny": [`  
>          `"git push origin main", "git push --force", "git push -f",`  
>          `"create_or_update_file", "push_files", "delete_file"`  
>        `]`  
>      `}`  
>    `}`

The token itself stays in `.env`; settings.json only names the variable. The deny list names three git commands and the three GitHub tools that write to a repository without a pull request: create\_or\_update\_file, push\_files and delete\_file. Leave Project 5's RULES.md where it is; the handout's step 3 replaces it.  
**Common problems.**

> * *macOS refuses to run it.* In the terminal, in p06, run `xattr -d com.apple.quarantine github-mcp-server`, then try again.  
> * *The version printed is not 2.0.2.* Another release was downloaded. Delete it and download from the 2.0.2 release page above.  
> * *The wizard says settings.json holds the token.* The token's value was pasted into settings.json. Put back \${GITHUB\_PERSONAL\_ACCESS\_TOKEN}; the value lives in `.env` only.  
> * *The wizard says settings.json is not valid JSON.* A quote or comma is missing. Compare it with the file above, character by character.  
> * *The wizard says the server does not answer.* The token line in `.env` is missing or wrong (step 3), or the file is not beside harness.py.

#### **5\. Your copy of the code**

**What it is for.** The code your harness edits and tests is a copy of your repository (step 2\) on your laptop, inside p06 beside harness.py. This step clones it, builds its Python environment, runs the tests once, and starts the image server once. You do it in class, so the first time you see thumbor the staff are in the room.  
**How it works.** The clone is a folder named p06-\<your login\> with the repository's history inside it. thumbor needs Python 3.12 or newer and a few native extensions compiled with a C compiler; they live in a Python environment inside the clone, .venv, so nothing is installed system-wide. The test suite is about 700 tests and runs in under a minute. Up to a dozen fail, depending on which of gifsicle, jpegtran and ffmpeg you have; on a laptop without gifsicle, jpegtran and ffmpeg; AGENTS.md lists them, and none is a defect of yours. The suite command leaves out test\_sentry and a speed-timeout test, which fail everywhere at the course's pinned commit. The server reads course/thumbor.conf, which points it at the course pictures, and answers a URL with a picture.  
**Do this.**

> 1. In your Terminal, in p06, clone your repository, your GitHub login in place of \<your login\>:  
>    `gh repo clone <your login>/p06-<your login>`  
> 2. Install a C compiler if you have none: thumbor's own filters are written in C, and the install below compiles them. Run xcode-select \--install once and wait for it to finish.  
> 3. Go in and make the environment. If `python3` is older than 3.12, use any newer one in its place, python3.12 or python3.14.  
>    `cd p06-<your login>`  
>    `python3 -m venv .venv`  
>    `source .venv/bin/activate`  
>    `python -m pip install -U pip setuptools wheel`  
>    `pip install -e ".[tests,opencv,extra-libs]"`  
>    `python setup.py build_ext -i`  
> 4. Run the suite once:  
>    `python -m pytest tests -q -p no:cacheprovider -p no:tldr --ignore=tests/detectors --ignore=tests/integration_tests --deselect tests/error_handlers/test_sentry.py::SentryTestCase::test_when_error_occurs_should_have_called_client --deselect tests/loaders/test_http_loader.py::HttpCurlTimeoutLoaderTestCase::test_load_with_speed_timeout`

It is the command in AGENTS.md. About 700 pass. Without gifsicle, jpegtran and ffmpeg up to a dozen fail, depending on which of gifsicle, jpegtran and ffmpeg you have;: the GIF tests, the cover and result-storage tests that load a GIF, and tests/test\_doctor.py. AGENTS.md lists every one; none is a defect.

> 5. Start the server and look at a picture:  
>    `python -m thumbor.server -p 8888 -c course/thumbor.conf -l error`

Open http://localhost:8888/unsafe/300x200/example.jpg in your browser. A picture appears. Stop the server with Ctrl+C.  
**Common problems.**

> * *pip install or build\_ext stops with no compiler.* Install one (step 2), then run the line that stopped again.  
> * *pip says the Python is too old.* thumbor needs 3.12 or newer. Install it from python.org and make the environment again with it.  
> * *The GIF tests fail.* gifsicle is missing: brew install gifsicle. Optional, except for the GIF issue on the menu.  
> * *The server says the port is in use.* Another server holds 8888\. Stop it, or start on another port and change only the port in the URL.  
> * *The picture does not appear.* The server was started outside the clone, or without \-c course/thumbor.conf. Start it from the clone's top folder with the line above.

## **Windows**

### **Part A: mark for attendance (in class)**

#### **Mark for attendance**

Your in-person attendance is worth 2 points of your assignment grade. There are two ways to mark attendance, both using the Wizard:

##### **A. Wizard TUI**

> 1. In your PowerShell:  
>    `python3 wizard.py`  
> 2. Choose Attendance

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-1.png)

> 3. Type in the attendance code, then press enter

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-2.png)

> 4. Confirmation message

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-3.png)

##### **B. Wizard CLI**

`python3 wizard.py attendance <code>`

### **Part 1: your harness, your repository and the code (every student)**

#### **1\. Your Project 5 harness**

**What it is for.** Your harness is the agent you built in Projects 3 to 5: harness.py, systemprompt.md (its system prompt) and the skills folder. In Project 5 it ran inside your codespace. Project 6 runs on your laptop, in a folder of its own named p06, because the code you fix and the tests you run live there too. This step brings the harness down and gives it its keys.  
**How it works.** The codespace is a computer in the cloud; `gh codespace cp` copies files between it and your laptop over the same connection VS Code uses. Your codespace's name is on github.com/codespaces. In the codespace the harness read its model's address and key from two environment variables the codespace set, PURPLE\_BASE\_URL and PURPLE\_API\_KEY. On your laptop nothing sets them, so they go in the file `.env` beside harness.py, and the harness has to read that file.  
**Do this.**

> 1. On your laptop, make a folder named p06 and open a PowerShell in it.  
> 2. Find your codespace's name at https://github.com/codespaces. It looks like orange-yodel-576g7xq5rpj344r: two words and a code. `gh codespace list` prints it; if there are several, pick the one you used last (the most recent in `gh codespace list`).  
> 3. Run, with that name in place of \<codespace\>:  
>    `gh codespace cp -e -r -c <codespace> remote:/workspaces/cse490-p05-starter/harness .`

A folder named harness appears in p06 with harness.py, systemprompt.md and the skills folder inside it: move everything inside it up into p06, so harness.py sits beside .env. RULES.md may come along from Project 5; step 4 replaces it with settings.json, so leave it alone until the handout says to delete it.

> 4. Make a file named `.env` in p06 with these lines, your Purple key from purple.uw.edu (Project 5's step 4\) in place of \<your Purple key\>:  
>    `PURPLE_BASE_URL=https://apim-n1ai-usw2-065882797.azure-api.net/openai/v1`  
>    `PURPLE_API_KEY=<your Purple key>`

If your harness.py reads the address and key under other names, use those names.

> 5. Give your harness its own Python environment in p06, with a Python of 3.10 or newer (the Mac's built-in `python3` is 3.9 and cannot install mcp, and a Homebrew Python refuses to install into itself): `py -3.12 -m venv .venv-harness; .venv-harness\Scripts\pip install python-dotenv mcp requests` (any newer Python in place of 3.12). From here on, run the harness with that environment's Python: .venv-harness\\Scripts\\python harness.py.  
> 6. If your harness reads only the environment and not `.env`, ask the LiteLLM chat in VS Code: "Read harness.py. At startup, load the variables in `.env` beside it into the environment when they are not set already. Change nothing else." Read the change before you accept it.

**Common problems.**

> * *gh says there is no codespace.* Start it once from github.com/codespaces, then run the copy again; a stopped codespace cannot be copied from.  
> * *The copy prints nothing for minutes.* A stopped codespace is starting; wait, or press Ctrl+C and run the copy again. If it fails twice, download the files from the codespace's Explorer instead.  
> * *A folder named harness appeared inside p06.* Move everything inside it up into p06, so harness.py sits beside .env.  
> * *I do not have the GitHub command line.* Install gh from cli.github.com and run `gh auth login`, or download harness.py, systemprompt.md and the skills folder from the codespace's Explorer (right-click, Download) into p06.  
> * *I lost my Purple key.* On purple.uw.edu open Settings, API Projects, your CSE490-P05 project: the Primary Key is there.  
> * *The harness answers with a 401\.* The key in `.env` is wrong or has a stray space. Copy it again.

#### **2\. Your repository**

**What it is for.** Project 6 happens in a repository of your own on GitHub: a private copy of thumbor, the image server, named p06-\<your login\> under your own account. It carries the five issues on the menu, and the handout has you fix three of them. It is thumbor as it was in September 2026, with its full history, before four of the five bugs were fixed in the real project; the fifth is a feature that does not exist yet. Your harness pushes branches and opens pull requests there, and the course grader reads it. Nothing is created in the course organisation, so nobody has to approve anything.  
**How it works.** The course starter, cse490A2/cse490-p06-starter, is a public template repository. GitHub can copy a template into a new repository under your account in one command, then it copies the files in the background for a minute. A copy made from a template has no link back to the starter, so a pull request you open stays in your repository. It also keeps none of thumbor's history, so the wizard pushes the starter's full history over the copy, and git blame and git log work the way the lecture shows. The five issues are not part of a template copy either, so the wizard files them from the starter's course/issues.json. Under each of the four real ones it posts the conversation from thumbor's own report, so you and your harness can read what the reporter and the maintainers said. It invites the course grader to read the repository so your pull requests can be graded.  
**Do this.**

> 1. Install the GitHub command line, gh, from cli.github.com if you do not have it (`winget install --id GitHub.cli`), and git from git-scm.com if `git --version` does not answer. In your PowerShell run `gh auth login`: pick GitHub.com, HTTPS, and sign in with a web browser. That account is the one the repository is made under.  
> 2. In the wizard, pick Project 6, open the step "Your repository" and choose "Create the repository now". It makes p06-\<your login\> from the template, waits for the copy, pushes thumbor's history, files the five issues with their conversations and invites the grader, printing each step. The history push takes about a minute.  
> 3. Without the wizard, you still need the wizard folder for its script: download https://github.com/cse490A2/cse490-published/releases/download/wizard/wizard-cse490.zip once and unpack it, the same zip Option 1 uses. In your p06 folder run, with your GitHub login in place of \<your login\>:  
>    `gh repo create p06-<your login> --private --template cse490A2/cse490-p06-starter`

then, once https://github.com/\<your login\>/p06-\<your login\> shows the code, run the wizard's script to push the history, file the issues and invite the grader:  
`python3 ~/Downloads/wizard/packs/p06/10-repo/make_repo.py`  
(the p06 pack is in the wizard folder once the wizard has run with Project 6 open; \<wizard folder\> is wherever you unpacked it)

> 4. Open https://github.com/\<your login\>/p06-\<your login\>/issues in the browser: five issues, each labelled menu, four of them with comments copied from the thumbor project.

**Common problems.**

> * *gh repo create says the name already exists.* Fine: go on to the wizard's script, which adds only what is missing.  
> * *gh is signed in as someone else.* The repository is made under the signed-in account. Run `gh auth login` again as the account you want.  
> * *The repository is there but empty.* GitHub is still copying the template. Wait a minute and look again.  
> * *A repository named p06-\<your login\> already exists under my account.* The script leaves it alone and only adds what is missing: the history, the issues, their conversations, the grader.  
> * *The wizard says the repository has no history.* git was not installed when the repository was made. Install git, then pick "Create the repository now" again.  
> * *GitHub asked the course staff to approve a token.* You made the token with the course organisation as its owner. That is the next step's mistake, not this one's: the owner is your own account.

#### **3\. GitHub token**

**What it is for.** Your harness needs its own key to your repository: a fine-grained personal access token, made on github.com, that can reach p06-\<your login\> and nothing else. The GitHub MCP server (step 4\) sends it with every request, the way your course key goes to the gateway. GitHub has no command for making one, so you make it in the browser; the wizard tests what it can reach.  
**How it works.** A fine-grained token is tied to one owner and a list of repositories, with a permission per kind of thing. Its owner is the account that holds the repository: your own account (step 2), not the course organisation. A token owned by an organisation needs an administrator's approval; one owned by you needs nobody's. The token is shown once, when it is made, and goes in `.env` beside your harness as GITHUB\_PERSONAL\_ACCESS\_TOKEN. The wizard asks GitHub three questions with it: can it read your repository, can it write to it, can it see any other repository. The answers must be yes, yes, no.  
**Do this.**

> 1. On github.com, click your profile picture, then Settings, Developer settings, Personal access tokens, Fine-grained tokens, Generate new token. Or open https://github.com/settings/personal-access-tokens/new.  
> 2. Token name: cse490-p06. Expiration: 90 days. Resource owner: your own account, not the course organisation.  
> 3. Under Repository access choose "Only select repositories" and pick p06-\<your login\>. One repository, no more.  
> 4. Under Repository permissions set Contents to Read and write, Issues to Read and write, and Pull requests to Read and write. Metadata becomes Read on its own. Leave everything else at No access.  
> 5. Click Generate token. GitHub shows it once, a long string starting with github\_pat\_. Copy the whole thing now.  
> 6. Open `.env` in your p06 folder (step 1\) and add this line, your token in place of \<your token\>, then save:  
>    `GITHUB_PERSONAL_ACCESS_TOKEN=<your token>`

**Common problems.**

> * *I used `gh auth token` instead.* That is a different kind of token: it reaches every repository you have, so the wizard's third check fails. Make the fine-grained one above; it starts with github\_pat\_.  
> * *The wizard says the token sees other repositories.* "All repositories" was chosen, or more than one was picked. Delete that token on github.com and make a new one with only p06-\<your login\>.  
> * *The wizard says the token cannot write.* Contents was left at Read. Edit the token on github.com: Contents, Issues and Pull requests to Read and write.  
> * *GitHub says the token is unknown (401).* A character was lost when pasting, or the token was deleted. Paste it again whole, or make a new one.  
> * *I closed the page before copying.* The token cannot be shown again. Delete it and make another.  
> * *The resource owner list shows cse490A2.* Pick your own account anyway. The repository is yours.

#### **4\. GitHub MCP server**

**What it is for.** The GitHub MCP server is the program that gives your harness GitHub's tools: read an issue, open a pull request, read its diff, post a review. It is the same kind of server as Blender's in Project 5, and your harness connects to it the same way, over a pipe, from an entry in settings.json.  
**How it works.** The server is one file, github-mcp-server, released by GitHub; the course pins release 2.0.2. Your harness starts it with the command `github-mcp-server stdio` and talks to it over standard input and output. The server reads your token (step 3\) from the environment variable GITHUB\_PERSONAL\_ACCESS\_TOKEN, which your harness passes it from .env. settings.json names the server, so the harness knows to start it; it is the same file shape Claude Code and Codex read, with the servers under mcpServers and the git commands and GitHub tools the harness must refuse under permissions. Project 5's RULES.md did this job as prose; in the handout's step 3 your harness switches to settings.json and RULES.md goes away.  
**Do this.**

> 1. Download github-mcp-server\_Windows\_x86\_64.zip from https://github.com/github/github-mcp-server/releases/tag/v2.0.2.  
> 2. Right-click it and choose Extract All. Move the file github-mcp-server.exe into your p06 folder (step 1), beside harness.py.  
> 3. Check it in your PowerShell, in p06: `.\github-mcp-server.exe --version` prints Version: 2.0.2 among its lines.  
> 4. Make a file named settings.json in p06, beside harness.py, with this in it:  
>    `{`  
>      `"mcpServers": {`  
>        `"github": {`  
>          `"command": ".\\github-mcp-server.exe",`  
>          `"args": ["stdio"],`  
>          `"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"}`  
>        `}`  
>      `},`  
>      `"permissions": {`  
>        `"deny": [`  
>          `"git push origin main", "git push --force", "git push -f",`  
>          `"create_or_update_file", "push_files", "delete_file"`  
>        `]`  
>      `}`  
>    `}`

The token itself stays in `.env`; settings.json only names the variable. The deny list names three git commands and the three GitHub tools that write to a repository without a pull request: create\_or\_update\_file, push\_files and delete\_file. Leave Project 5's RULES.md where it is; the handout's step 3 replaces it.  
**Common problems.**

> * *Windows protected your PC.* Click More info, then Run anyway; or right-click the file, Properties, tick Unblock.  
> * *The version printed is not 2.0.2.* Another release was downloaded. Delete it and download from the 2.0.2 release page above.  
> * *The wizard says settings.json holds the token.* The token's value was pasted into settings.json. Put back \${GITHUB\_PERSONAL\_ACCESS\_TOKEN}; the value lives in `.env` only.  
> * *The wizard says settings.json is not valid JSON.* A quote or comma is missing. Compare it with the file above, character by character.  
> * *The wizard says the server does not answer.* The token line in `.env` is missing or wrong (step 3), or the file is not beside harness.py.

#### **5\. Your copy of the code**

**What it is for.** The code your harness edits and tests is a copy of your repository (step 2\) on your laptop, inside p06 beside harness.py. This step clones it, builds its Python environment, runs the tests once, and starts the image server once. You do it in class, so the first time you see thumbor the staff are in the room.  
**How it works.** The clone is a folder named p06-\<your login\> with the repository's history inside it. thumbor needs Python 3.12 or newer and a few native extensions compiled with a C compiler; they live in a Python environment inside the clone, .venv, so nothing is installed system-wide. The test suite is about 700 tests and runs in under a minute. Up to a dozen fail, depending on which of gifsicle, jpegtran and ffmpeg you have; on a laptop without gifsicle, jpegtran and ffmpeg; AGENTS.md lists them, and none is a defect of yours. The suite command leaves out test\_sentry and a speed-timeout test, which fail everywhere at the course's pinned commit. The server reads course/thumbor.conf, which points it at the course pictures, and answers a URL with a picture.  
**Do this.**

> 1. In your PowerShell, in p06, clone your repository, your GitHub login in place of \<your login\>:  
>    `gh repo clone <your login>/p06-<your login>`  
> 2. Install a C compiler if you have none: thumbor's own filters are written in C, and the install below compiles them. Open https://visualstudio.microsoft.com/visual-cpp-build-tools/, download and run the installer, and tick the workload "Desktop development with C++". It is about 6 GB. When it finishes, open a new PowerShell.  
> 3. Go in and make the environment. Use `py` \-3 in place of python3.  
>    `cd p06-<your login>`  
>    `py -3 -m venv .venv`  
>    `.venv\Scripts\activate`  
>    `python -m pip install -U pip setuptools wheel`  
>    `pip install -e ".[tests,opencv,extra-libs]"`  
>    `python setup.py build_ext -i`  
> 4. Run the suite once:  
>    `python -m pytest tests -q -p no:cacheprovider -p no:tldr --ignore=tests/detectors --ignore=tests/integration_tests --deselect tests/error_handlers/test_sentry.py::SentryTestCase::test_when_error_occurs_should_have_called_client --deselect tests/loaders/test_http_loader.py::HttpCurlTimeoutLoaderTestCase::test_load_with_speed_timeout`

It is the command in AGENTS.md. About 700 pass. Without gifsicle, jpegtran and ffmpeg up to a dozen fail, depending on which of gifsicle, jpegtran and ffmpeg you have;: the GIF tests, the cover and result-storage tests that load a GIF, and tests/test\_doctor.py. AGENTS.md lists every one; none is a defect.

> 5. Start the server and look at a picture:  
>    `python -m thumbor.server -p 8888 -c course/thumbor.conf -l error`

Open http://localhost:8888/unsafe/300x200/example.jpg in your browser. A picture appears. Stop the server with Ctrl+C.  
**Common problems.**

> * *pip install or build\_ext stops with no compiler, saying Microsoft Visual C++ 14.0 or greater is required.* Install one (step 2), open a new PowerShell, then run the line that stopped again.  
> * *pip says the Python is too old.* thumbor needs 3.12 or newer. Install it from python.org and make the environment again with it.  
> * *The GIF tests fail.* gifsicle is missing: gifsicle for Windows from eternallybored.org/misc/gifsicle. Optional, except for the GIF issue on the menu.  
> * *The server says the port is in use.* Another server holds 8888\. Stop it, or start on another port and change only the port in the URL.  
> * *The picture does not appear.* The server was started outside the clone, or without \-c course/thumbor.conf. Start it from the clone's top folder with the line above.

## **Linux**

### **Part A: mark for attendance (in class)**

#### **Mark for attendance**

Your in-person attendance is worth 2 points of your assignment grade. There are two ways to mark attendance, both using the Wizard:

##### **A. Wizard TUI**

> 1. In your terminal:  
>    `python3 wizard.py`  
> 2. Choose Attendance

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-1.png)

> 3. Type in the attendance code, then press enter

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-2.png)

> 4. Confirmation message

   
![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P06/images/setup-3.png)

##### **B. Wizard CLI**

`python3 wizard.py attendance <code>`

### **Part 1: your harness, your repository and the code (every student)**

#### **1\. Your Project 5 harness**

**What it is for.** Your harness is the agent you built in Projects 3 to 5: harness.py, systemprompt.md (its system prompt) and the skills folder. In Project 5 it ran inside your codespace. Project 6 runs on your laptop, in a folder of its own named p06, because the code you fix and the tests you run live there too. This step brings the harness down and gives it its keys.  
**How it works.** The codespace is a computer in the cloud; `gh codespace cp` copies files between it and your laptop over the same connection VS Code uses. Your codespace's name is on github.com/codespaces. In the codespace the harness read its model's address and key from two environment variables the codespace set, PURPLE\_BASE\_URL and PURPLE\_API\_KEY. On your laptop nothing sets them, so they go in the file `.env` beside harness.py, and the harness has to read that file.  
**Do this.**

> 1. On your laptop, make a folder named p06 and open a terminal in it.  
> 2. Find your codespace's name at https://github.com/codespaces. It looks like orange-yodel-576g7xq5rpj344r: two words and a code. `gh codespace list` prints it; if there are several, pick the one you used last (the most recent in `gh codespace list`).  
> 3. Run, with that name in place of \<codespace\>:  
>    `gh codespace cp -e -r -c <codespace> remote:/workspaces/cse490-p05-starter/harness .`

A folder named harness appears in p06 with harness.py, systemprompt.md and the skills folder inside it: move everything inside it up into p06, so harness.py sits beside .env. RULES.md may come along from Project 5; step 4 replaces it with settings.json, so leave it alone until the handout says to delete it.

> 4. Make a file named `.env` in p06 with these lines, your Purple key from purple.uw.edu (Project 5's step 4\) in place of \<your Purple key\>:  
>    `PURPLE_BASE_URL=https://apim-n1ai-usw2-065882797.azure-api.net/openai/v1`  
>    `PURPLE_API_KEY=<your Purple key>`

If your harness.py reads the address and key under other names, use those names.

> 5. Give your harness its own Python environment in p06, with a Python of 3.10 or newer (the Mac's built-in `python3` is 3.9 and cannot install mcp, and a Homebrew Python refuses to install into itself): `python3.12 -m venv .venv-harness && .venv-harness/bin/pip install python-dotenv mcp requests` (any newer Python in place of 3.12). From here on, run the harness with that environment's Python: .venv-harness/bin/python harness.py.  
> 6. If your harness reads only the environment and not `.env`, ask the LiteLLM chat in VS Code: "Read harness.py. At startup, load the variables in `.env` beside it into the environment when they are not set already. Change nothing else." Read the change before you accept it.

**Common problems.**

> * *gh says there is no codespace.* Start it once from github.com/codespaces, then run the copy again; a stopped codespace cannot be copied from.  
> * *The copy prints nothing for minutes.* A stopped codespace is starting; wait, or press Ctrl+C and run the copy again. If it fails twice, download the files from the codespace's Explorer instead.  
> * *A folder named harness appeared inside p06.* Move everything inside it up into p06, so harness.py sits beside .env.  
> * *I do not have the GitHub command line.* Install gh from cli.github.com and run `gh auth login`, or download harness.py, systemprompt.md and the skills folder from the codespace's Explorer (right-click, Download) into p06.  
> * *I lost my Purple key.* On purple.uw.edu open Settings, API Projects, your CSE490-P05 project: the Primary Key is there.  
> * *The harness answers with a 401\.* The key in `.env` is wrong or has a stray space. Copy it again.

#### **2\. Your repository**

**What it is for.** Project 6 happens in a repository of your own on GitHub: a private copy of thumbor, the image server, named p06-\<your login\> under your own account. It carries the five issues on the menu, and the handout has you fix three of them. It is thumbor as it was in September 2026, with its full history, before four of the five bugs were fixed in the real project; the fifth is a feature that does not exist yet. Your harness pushes branches and opens pull requests there, and the course grader reads it. Nothing is created in the course organisation, so nobody has to approve anything.  
**How it works.** The course starter, cse490A2/cse490-p06-starter, is a public template repository. GitHub can copy a template into a new repository under your account in one command, then it copies the files in the background for a minute. A copy made from a template has no link back to the starter, so a pull request you open stays in your repository. It also keeps none of thumbor's history, so the wizard pushes the starter's full history over the copy, and git blame and git log work the way the lecture shows. The five issues are not part of a template copy either, so the wizard files them from the starter's course/issues.json. Under each of the four real ones it posts the conversation from thumbor's own report, so you and your harness can read what the reporter and the maintainers said. It invites the course grader to read the repository so your pull requests can be graded.  
**Do this.**

> 1. Install the GitHub command line, gh, from cli.github.com if you do not have it (your distribution's package), and git from git-scm.com if `git --version` does not answer. In your terminal run `gh auth login`: pick GitHub.com, HTTPS, and sign in with a web browser. That account is the one the repository is made under.  
> 2. In the wizard, pick Project 6, open the step "Your repository" and choose "Create the repository now". It makes p06-\<your login\> from the template, waits for the copy, pushes thumbor's history, files the five issues with their conversations and invites the grader, printing each step. The history push takes about a minute.  
> 3. Without the wizard, you still need the wizard folder for its script: download https://github.com/cse490A2/cse490-published/releases/download/wizard/wizard-cse490.zip once and unpack it, the same zip Option 1 uses. In your p06 folder run, with your GitHub login in place of \<your login\>:  
>    `gh repo create p06-<your login> --private --template cse490A2/cse490-p06-starter`

then, once https://github.com/\<your login\>/p06-\<your login\> shows the code, run the wizard's script to push the history, file the issues and invite the grader:  
`python3 ~/Downloads/wizard/packs/p06/10-repo/make_repo.py`  
(the p06 pack is in the wizard folder once the wizard has run with Project 6 open; \<wizard folder\> is wherever you unpacked it)

> 4. Open https://github.com/\<your login\>/p06-\<your login\>/issues in the browser: five issues, each labelled menu, four of them with comments copied from the thumbor project.

**Common problems.**

> * *gh repo create says the name already exists.* Fine: go on to the wizard's script, which adds only what is missing.  
> * *gh is signed in as someone else.* The repository is made under the signed-in account. Run `gh auth login` again as the account you want.  
> * *The repository is there but empty.* GitHub is still copying the template. Wait a minute and look again.  
> * *A repository named p06-\<your login\> already exists under my account.* The script leaves it alone and only adds what is missing: the history, the issues, their conversations, the grader.  
> * *The wizard says the repository has no history.* git was not installed when the repository was made. Install git, then pick "Create the repository now" again.  
> * *GitHub asked the course staff to approve a token.* You made the token with the course organisation as its owner. That is the next step's mistake, not this one's: the owner is your own account.

#### **3\. GitHub token**

**What it is for.** Your harness needs its own key to your repository: a fine-grained personal access token, made on github.com, that can reach p06-\<your login\> and nothing else. The GitHub MCP server (step 4\) sends it with every request, the way your course key goes to the gateway. GitHub has no command for making one, so you make it in the browser; the wizard tests what it can reach.  
**How it works.** A fine-grained token is tied to one owner and a list of repositories, with a permission per kind of thing. Its owner is the account that holds the repository: your own account (step 2), not the course organisation. A token owned by an organisation needs an administrator's approval; one owned by you needs nobody's. The token is shown once, when it is made, and goes in `.env` beside your harness as GITHUB\_PERSONAL\_ACCESS\_TOKEN. The wizard asks GitHub three questions with it: can it read your repository, can it write to it, can it see any other repository. The answers must be yes, yes, no.  
**Do this.**

> 1. On github.com, click your profile picture, then Settings, Developer settings, Personal access tokens, Fine-grained tokens, Generate new token. Or open https://github.com/settings/personal-access-tokens/new.  
> 2. Token name: cse490-p06. Expiration: 90 days. Resource owner: your own account, not the course organisation.  
> 3. Under Repository access choose "Only select repositories" and pick p06-\<your login\>. One repository, no more.  
> 4. Under Repository permissions set Contents to Read and write, Issues to Read and write, and Pull requests to Read and write. Metadata becomes Read on its own. Leave everything else at No access.  
> 5. Click Generate token. GitHub shows it once, a long string starting with github\_pat\_. Copy the whole thing now.  
> 6. Open `.env` in your p06 folder (step 1\) and add this line, your token in place of \<your token\>, then save:  
>    `GITHUB_PERSONAL_ACCESS_TOKEN=<your token>`

**Common problems.**

> * *I used `gh auth token` instead.* That is a different kind of token: it reaches every repository you have, so the wizard's third check fails. Make the fine-grained one above; it starts with github\_pat\_.  
> * *The wizard says the token sees other repositories.* "All repositories" was chosen, or more than one was picked. Delete that token on github.com and make a new one with only p06-\<your login\>.  
> * *The wizard says the token cannot write.* Contents was left at Read. Edit the token on github.com: Contents, Issues and Pull requests to Read and write.  
> * *GitHub says the token is unknown (401).* A character was lost when pasting, or the token was deleted. Paste it again whole, or make a new one.  
> * *I closed the page before copying.* The token cannot be shown again. Delete it and make another.  
> * *The resource owner list shows cse490A2.* Pick your own account anyway. The repository is yours.

#### **4\. GitHub MCP server**

**What it is for.** The GitHub MCP server is the program that gives your harness GitHub's tools: read an issue, open a pull request, read its diff, post a review. It is the same kind of server as Blender's in Project 5, and your harness connects to it the same way, over a pipe, from an entry in settings.json.  
**How it works.** The server is one file, github-mcp-server, released by GitHub; the course pins release 2.0.2. Your harness starts it with the command `github-mcp-server stdio` and talks to it over standard input and output. The server reads your token (step 3\) from the environment variable GITHUB\_PERSONAL\_ACCESS\_TOKEN, which your harness passes it from .env. settings.json names the server, so the harness knows to start it; it is the same file shape Claude Code and Codex read, with the servers under mcpServers and the git commands and GitHub tools the harness must refuse under permissions. Project 5's RULES.md did this job as prose; in the handout's step 3 your harness switches to settings.json and RULES.md goes away.  
**Do this.**

> 1. Download github-mcp-server\_Linux\_x86\_64.tar.gz from https://github.com/github/github-mcp-server/releases/tag/v2.0.2.  
> 2. Unpack it with tar. Move the file github-mcp-server into your p06 folder (step 1), beside harness.py.  
> 3. Check it in your terminal, in p06: `./github-mcp-server --version` prints Version: 2.0.2 among its lines.  
> 4. Make a file named settings.json in p06, beside harness.py, with this in it:  
>    `{`  
>      `"mcpServers": {`  
>        `"github": {`  
>          `"command": "./github-mcp-server",`  
>          `"args": ["stdio"],`  
>          `"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"}`  
>        `}`  
>      `},`  
>      `"permissions": {`  
>        `"deny": [`  
>          `"git push origin main", "git push --force", "git push -f",`  
>          `"create_or_update_file", "push_files", "delete_file"`  
>        `]`  
>      `}`  
>    `}`

The token itself stays in `.env`; settings.json only names the variable. The deny list names three git commands and the three GitHub tools that write to a repository without a pull request: create\_or\_update\_file, push\_files and delete\_file. Leave Project 5's RULES.md where it is; the handout's step 3 replaces it.  
**Common problems.**

> * *Permission denied.* In the terminal, in p06, run `chmod +x github-mcp-server`, then try again.  
> * *The version printed is not 2.0.2.* Another release was downloaded. Delete it and download from the 2.0.2 release page above.  
> * *The wizard says settings.json holds the token.* The token's value was pasted into settings.json. Put back \${GITHUB\_PERSONAL\_ACCESS\_TOKEN}; the value lives in `.env` only.  
> * *The wizard says settings.json is not valid JSON.* A quote or comma is missing. Compare it with the file above, character by character.  
> * *The wizard says the server does not answer.* The token line in `.env` is missing or wrong (step 3), or the file is not beside harness.py.

#### **5\. Your copy of the code**

**What it is for.** The code your harness edits and tests is a copy of your repository (step 2\) on your laptop, inside p06 beside harness.py. This step clones it, builds its Python environment, runs the tests once, and starts the image server once. You do it in class, so the first time you see thumbor the staff are in the room.  
**How it works.** The clone is a folder named p06-\<your login\> with the repository's history inside it. thumbor needs Python 3.12 or newer and a few native extensions compiled with a C compiler; they live in a Python environment inside the clone, .venv, so nothing is installed system-wide. The test suite is about 700 tests and runs in under a minute. Up to a dozen fail, depending on which of gifsicle, jpegtran and ffmpeg you have; on a laptop without gifsicle, jpegtran and ffmpeg; AGENTS.md lists them, and none is a defect of yours. The suite command leaves out test\_sentry and a speed-timeout test, which fail everywhere at the course's pinned commit. The server reads course/thumbor.conf, which points it at the course pictures, and answers a URL with a picture.  
**Do this.**

> 1. In your terminal, in p06, clone your repository, your GitHub login in place of \<your login\>:  
>    `gh repo clone <your login>/p06-<your login>`  
> 2. Install a C compiler if you have none: thumbor's own filters are written in C, and the install below compiles them. Run sudo apt-get install build-essential python3-dev.  
> 3. Go in and make the environment. If `python3` is older than 3.12, use any newer one in its place, python3.12 or python3.14.  
>    `cd p06-<your login>`  
>    `python3 -m venv .venv`  
>    `source .venv/bin/activate`  
>    `python -m pip install -U pip setuptools wheel`  
>    `pip install -e ".[tests,opencv,extra-libs]"`  
>    `python setup.py build_ext -i`  
> 4. Run the suite once:  
>    `python -m pytest tests -q -p no:cacheprovider -p no:tldr --ignore=tests/detectors --ignore=tests/integration_tests --deselect tests/error_handlers/test_sentry.py::SentryTestCase::test_when_error_occurs_should_have_called_client --deselect tests/loaders/test_http_loader.py::HttpCurlTimeoutLoaderTestCase::test_load_with_speed_timeout`

It is the command in AGENTS.md. About 700 pass. Without gifsicle, jpegtran and ffmpeg up to a dozen fail, depending on which of gifsicle, jpegtran and ffmpeg you have;: the GIF tests, the cover and result-storage tests that load a GIF, and tests/test\_doctor.py. AGENTS.md lists every one; none is a defect.

> 5. Start the server and look at a picture:  
>    `python -m thumbor.server -p 8888 -c course/thumbor.conf -l error`

Open http://localhost:8888/unsafe/300x200/example.jpg in your browser. A picture appears. Stop the server with Ctrl+C.  
**Common problems.**

> * *pip install or build\_ext stops with no compiler.* Install one (step 2), then run the line that stopped again.  
> * *pip says the Python is too old.* thumbor needs 3.12 or newer. Install it from python.org and make the environment again with it.  
> * *The GIF tests fail.* gifsicle is missing: sudo apt-get install gifsicle. Optional, except for the GIF issue on the menu.  
> * *The server says the port is in use.* Another server holds 8888\. Stop it, or start on another port and change only the port in the URL.  
> * *The picture does not appear.* The server was started outside the clone, or without \-c course/thumbor.conf. Start it from the clone's top folder with the line above.
