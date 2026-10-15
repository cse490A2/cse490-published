---
title: "P03: The Agent Harness"
parent: "Projects"
nav_order: 3
has_children: true
permalink: "/projects/P03/"
---

# Project 3: The Agent Harness

**Due: Tuesday 11:59 pm**  
Prerequisites: run the course setup wizard from the Prerequisites module in Canvas, or follow the [setup guide](SETUP.md) to do the same steps by hand.  
A model is an input-output machine: text in, text out. Everything an AI tool does beyond that lives in the harness: the program that feeds the model its task, runs the tools it asks for, and stops it when it's done. This week, you will write that harness. To help understand the mechanics of a harness, you'll use AI as a text-only tool rather than a full agent. The editor's agent mode is out of bounds this week. You are building that, and the industrial one arrives next week. Writing the puzzle's solver or fixing the testbench files by hand is out of bounds too. Every fix goes through your agent. This project will loosely follow the week's reading, [Let's write a harness](https://posts.oztamir.com/lets-write-a-harness-or-harness-engineering-101/).

## Instructions

1. In VS Code, open the VS Code LiteLLM chat window and `harness.py.` Your key and gateway address should already be populated in the .env file from setup. Off campus, connect the UW VPN (Husky OnNet) first: the gateway refuses every other connection.  
2. Prompt AI to convert the referenced harness pseudo code into python code. Your harness reads the gateway address, your key and the model name from .env (the four lines under Reference) and sends its requests to `https://llmproxy.cs.washington.edu/v1/chat/completions` with the key from .env and a model name exactly as your key's model list prints it (the setup guide's curl command shows the list). Use `external/haiku-5-5`.[^1]  
3. Once written, run the harness code and ask it to solve the puzzle in the untangle folder. It can only answer in text, so expect it to say it cannot open or run anything, or to guess.  
4. The model in your custom harness currently can't touch your files; it can only reply with text. Whenever the model needs to touch a file, it asks its harness. We will use JSON as the mutual communication language between the model and your harness, like {"command": "read\_file", "path": "..."}. Prompt LiteLLM to implement this:   
   1. *"Now add the capability to issue tool calls, starting with 'read\_file'. Do this by specifying a json object for each of these commands, and instruct the model to return a call to one of them when it wants to execute that command. Don't yet execute the command, just let me test that the model properly formats the command."*  
5. Verify the code generated. Ask your custom harness again to read untangle/README.md, and the model should output a JSON-formatted read\_file call. It should also respond with plain text when not passing the tool request. Use the suggested prompt if either fails:  
   1. *"Define a JSON schema for tool calls: an object with a required command field whose only allowed value is read\_file and a required path string. Make the harness validate every model reply against this schema. If a reply is not valid JSON or does not match the schema, send the model a message saying so."*  
6. Your harness can now recognize a read\_file request, but does nothing with it. Prompt LiteLLM Chat to generate code for the harness to act on a read\_file request:  
   1.  *"When the model's reply is a valid read\_file command, open that path, add the file's contents to the context as a message from the harness, and call the model again. Keep looping until the model replies with plain text. Do not add any other command yet."*  
7. If your agent can read untangle/README.md and untangle/graph.json, it knows the puzzle: a planar graph drawn with every node in the wrong place, one node moved per turn until no two edges cross, scored by the number of turns. Add write\_file and execute\_file into your harness, then have it write untangle/solve.py (two arguments: the graph file to read and the moves file to write), run it, run the judge, and keep going until the judge reports zero crossings. **IMPORTANT:** the addition of these tools will make your harness more capable and **dangerous**\! Before adding these tools, give your harness its rules. They live in systemprompt.md in the starter. Hook the file up in harness.py:  
   1\. At the top, read it once:  
       SYSTEM \= open("systemprompt.md").read()  
   2\. Start the context with it, before the loop:  
       context \= \[{"role": "system", "content": SYSTEM}\]  
   Your harness already sends the whole context on every call, so the rules go with every request. Restart the harness after any change to systemprompt.md.  
8. Then add write\_file and execute\_file, and make the harness print each command and wait for you to type yes before running it. execute\_file runs a file with the same Python that runs your harness (sys.executable), so the same harness works on Mac and Windows.  
9. Run the judge yourself. In the VS Code terminal, with the project's .venv selected, from the project folder: python untangle/check.py untangle/graph.json untangle/moves.json. It prints the crossings, which must be 0, and your turns.  
10. Watch your solver work. Same terminal, same folder: python untangle/view.py untangle/graph.json untangle/moves.json. A window opens with the tangled graph. Play runs your move list one turn at a time, Step takes one turn, Restart rewinds. If no window opens, or it opens blank, the same player opens in your browser by itself. The score is the number of turns: one move per node is the reference, and fewer is better.  
11. Open harness\_testbench.md and use your custom harness to address each mini-task. 

## Turnin

By Tuesday 11:59 pm:

* In VS Code, open the Command Palette (Cmd+Shift+P on Mac or Ctrl+Shift+P on Windows) and run CSE 490: Package for turn-in.   
* Upload P03-submission.zip and submit. 

## Grading

The course's automated grader reads your submission and checks that each step was properly followed. VS Code records your chats with the course models in logs/: \_chatlog.jsonl is the record, \_chatlog.md the readable view, and \_chatlog.json the switch. To start over, delete \_chatlog.jsonl and \_chatlog.md; deleting \_chatlog.json turns the recording off instead, and the grader needs it on. Every check is pass or fail. It does not judge code style, prompt wording, or how many tries it took. If you would like to delete a chat from the record, delete the two record files and redo the steps; the grader reads only what is in logs/ at turn-in. 

## Reference

**The chatbot loop from lecture:**  
context \= \[\]  
while True:  
    user \= input("\>\>\> ")  
    context.append(user)  
    reply \= call\_model(context)  
    print(reply)  
    context.append(reply)

**Reading the gateway from .env** (requests and python-dotenv are installed in the project's .venv by setup):  
from dotenv import load\_dotenv  
load\_dotenv()  
URL \= os.environ\["LITELLM\_BASE\_URL"\].rstrip("/") \+ "/v1/chat/completions"  
KEY \= os.environ\["LITELLM\_API\_KEY"\]  
MODEL \= "external/haiku-5-5"  
Then every request is requests.post(URL, headers={"Authorization": "Bearer " \+ KEY}, json={"model": MODEL, "messages": context}).

**systemprompt.md,**   
You are a coding agent.  
Work only inside this repo.  
Use only the tools you are given.  
Ask before anything destructive.  
Run the tests before claiming done.  
Stop when they pass.

**Switching the harness to Qwen**  
internal/Qwen3.6-35B-A3B costs nothing. Add this field to the JSON body of every request your harness sends, beside "model" and "messages":  
"extra\_body": {"chat\_template\_kwargs": {"enable\_thinking": false}}  
Then set "model" to "internal/Qwen3.6-35B-A3B".

**If your AI uses the litellm package**  
The litellm package reads the part of a model name before the slash as a provider, so it refuses external/haiku-5-5. Put litellm\_proxy/ in front of the name, litellm\_proxy/external/haiku-5-5, with api\_base set to the gateway address and api\_key to your key. The openai package needs no prefix: base\_url is the gateway address plus /v1. Through either package, the Qwen thinking-off field is nested once more: extra\_body={"extra\_body": {"chat\_template\_kwargs": {"enable\_thinking": false}}}. 

[^1]:  If you run out of credits on Haiku, you can switch to internal/Qwen3.6-35B-A3B. See Reference for instructions. 