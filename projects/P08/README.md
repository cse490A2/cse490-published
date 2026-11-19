---
title: "P08: Model Routing"
parent: "Projects"
nav_order: 8
has_children: true
permalink: "/projects/P08/"
---

# Project 8: Model Routing

**Due: Tuesday 11:59 pm**

Prerequisites: Complete the setup guide during class.

Decision models are LLMs built to pick between given options and provide an answer much faster than a normal model. This is done by removing the part of the LLM that generates text and replacing it with a small layer that scores each option. In this project, you'll use a decision model to check every response from one model and decide whether to route the prompt to another. Your harness has a router from the setup guide that asks the decider one question. You'll change it to ask two questions in one call: 1\) does the response contain code, and 2\) is the response high quality? High quality means backed by the files the model read. A response goes to the stronger model only when it has code and is low quality. Then you'll set the router's threshold from a benchmark.

We will use Qwen 3.6 as the model that responds to all requests, and Haiku 5.5 as the stronger model.

Note: this configuration is for educational purposes to demonstrate cascade routing.

![](https://raw.githubusercontent.com/cse490A2/cse490-published/main/projects/P08/images/handout-1.png)

## Instructions

1. Start the Strand decider server and your harness.  
2. Ask the coding agent in VS Code to change the router with the following prompt:  
   1. "Read `harness.py` and `settings.json`. Change the router to ask two questions in its one decider call. Change `router.question` to: 'Did the model read the files it needed before answering?' Add the setting `router.code_question`: 'Does the response contain program code?' Send both in the same request, named `quality` and `code`. Send the response to `router.fallback_model` only when `code` is at least 0.5 and `quality` is below `router.threshold`. Print both numbers in the `[router]` line. Write both to the `router_judge` trace record as `code` and `quality`. Keep one decider call for every response."  
3. Ask the harness the three test prompts. Prompts 1 and 2 stay with Qwen; prompt 3 goes to Haiku. If one lands on the wrong side, read its `code` and `quality` numbers in `trace.jsonl` and tune the wording of `router.question`.  
   1. "What is the default model in `settings.json`?"  
   2. "Read `harness.py` and write a short Python snippet that uses its setting helper to print the router threshold."  
   3. "Without reading any files, write Python that calls `harness.load_router_config()` and prints the result."  
2. Run the benchmark yourself to measure your threshold. From your harness folder, run:  
   1. python bench/sweep.py. It sends every prompt in bench/prompts.jsonl through your harness without calling Haiku. It records the two numbers for each response and counts how many prompts land on the side their label says at each threshold from 0.1 to 0.9. It saves the table to bench/sweep.txt.  
2. Set `router.threshold` to the value with the most prompts on the right side. On a tie, take the one that sends fewer prompts to Haiku. Run the three test prompts again.

## Turnin

Submit the following files to the Project 8 assignment in Canvas:

1. `settings.json` and `harness.py`, from your harness folder.  
2. `trace.jsonl`, holding your final run of the three test prompts.  
3. `bench/sweep.txt`, the threshold table from step 4\.

## Grading

A model will autograde your submission. It checks that the decider is asked both questions in one call about every response, that a response goes to Haiku only when `code` is at least 0.5 and `quality` is below the threshold, that every trace record holds both numbers, and that your threshold is the best one in your table. Every check is pass or fail. It does not judge your question wording or how many tries it took.

## Reference

The decider is a small model that compares a response against the text it is shown. It cannot run code or check a calculation; it can tell whether the names and values in the code appear in the files the agent read.

The setup guide's step 5 shows what the router sends the decider and what comes back. Its Appendix C lists the router's settings and fixes.

Out of bounds: removing the decider call, and hand-editing `trace.jsonl` or `bench/sweep.txt`.

If the decider server won't start, pair with a neighbour and submit your own harness and their trace. If your gateway key fails, submit what ran and rerun the Haiku side by the deadline.
