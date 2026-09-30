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
A model is an input-output machine: text in, text out. Everything an AI tool does beyond that lives in the harness: the program that feeds the model its task, runs the tools it asks for, and stops it when it's done. This week, you will write that harness. To help understand the mechanics of a harness, you'll use AI as a text-only tool rather than a full agent. This project will loosely follow the week's reading, [Let's write a harness](https://posts.oztamir.com/lets-write-a-harness-or-harness-engineering-101/).

## Instructions

1. In VS Code, open the VS Code LiteLLM chat window and `harness.py.` Your key and gateway address should already be populated in the .env file from setup.  
2. Prompt AI to convert the referenced harness pseudo code into python code. Once written, run the harness code. Try prompting it to run hello\_world.py.  
3. The model in your custom harness currently can't touch your files; it can only reply with text. Whenever the model needs to touch a file, it asks its harness. We will use JSON as the mutual communication language between the model and your harness, like {"command": "read\_file", "path": "..."}. Prompt LiteLLM to implement this:   
   1. *"Now add the capability to issue tool calls, starting with 'read\_file'. Do this by specifying a json object for each of these commands, and instruct the model to return a call to one of them when it wants to execute that command. Don't yet execute the command, just let me test that the model properly formats the command."*  
4. Verify the code generated. Ask your custom harness again to read hello\_world.py, and the model should output a JSON-formatted read\_file call. It should also respond with plain text when not passing the tool request. Use the suggested prompt if either fails:  
   1. *"Define a JSON schema for tool calls: an object with a required command field whose only allowed value is read\_file and a required path string. Make the harness validate every model reply against this schema. If a reply is not valid JSON or does not match the schema, send the model a message saying so."*  
5. Your harness can now recognize a read\_file request, but does nothing with it. Prompt LiteLLM Chat to generate code for the harness to act on a read\_file request:  
   1.  *"When the model's reply is a valid read\_file command, open that path, add the file's contents to the context as a message from the harness, and call the model again. Keep looping until the model replies with plain text. Do not add any other command yet."*  
6. If your agent can read hello\_world.py, then it may have noticed a bug in the program. Add write\_file and execute\_file into your harness, then have it fix the file and execute the code. **IMPORTANT:** the addition of these tools will make your harness more capable and **dangerous**\! When adding these tools, prompt LiteLLM Chat to include guardrails by confirming with the user before executing a write or execute command.  
7. Open harness\_testbench.md and use your custom harness to address each mini-task. 

## Turnin

By Tuesday 11:59 pm:

* In VS Code, open the Command Palette (Cmd+Shift+P on Mac or Ctrl+Shift+P on Windows) and run CSE 490: Package for turn-in.   
* Upload P03-submission.zip and submit. 

## Grading

The course's automated grader reads your submission and checks that each step was properly followed. VS Code records your chats with the course models in logs/. To start over, delete `_chatlog.jsonl` and `_chatlog.md` there. Every check is pass or fail. It does not judge code style, prompt wording, or how many tries it took. If you would like to delete 

## Reference

The chatbot loop from lecture:  
context \= \[\]  
while True:  
    user \= input("\>\>\> ")  
    context.append(user)  
    reply \= call\_model(context)  
    print(reply)  
    context.append(reply)

