---
title: "P07: A Team Upgrades Your Agent"
parent: "Projects"
nav_order: 7
has_children: true
permalink: "/projects/P07/"
---

# Project 7: A Team Upgrades Your Agent

**Due: Tuesday 11:59 pm**

Prerequisites: finish the setup guide first.

In this project, you add multi-agent capabilities to your harness. A /spawn command from your answer will starts a manager agent, which will splits a goal into tasks and starts one helper agent per task, all at once. You use the team to build eight new tools, and then you measure how well it answers a set of questions.

We will use external/haiku-5-5 as our model for our harness and multi-agents.

Run every command from your harness folder, with its Python environment on from setup.  `source .venv-harness/bin/activate`

## Instructions

1. So far your harness has been one agent. We'll now add the ability to spawn several agents from one harness session. A team of agents can split a job into pieces and work on them at the same moment. This is useful to divide and conquer a task without managing several agents yourself.  
     
   Let's consider an example of the proposed interface, `/spawn <goal>`:  
     
   `/spawn find why the gifv tests fail, edit only thumbor/engines/, and report what the error was, and how it was fixed.`  
     
   In the above example, the user is asking the harness to identify and fix a bug found in some project. For this assignment, we'll create a manager-helper style of orchestration. When /spawn is invoked, a manager is handed the goal and is responsible for delegating to helper agents. We can define the general behavior and strategy of agent deployment, or leave it up to the model to decide. We control how many helpers one call may start with a limit in `settings.json`.  
     
   Here's roughly how our orchestration will work:  
     
   `spawn(goal):`  
       `report = run_copy("manager", goal)`  
       `print(report)`  
     
   **`spawn`** runs when you type `/spawn <goal>` in the chat. It starts one manager and prints the manager's report.  
     
   `run_copy(role, task):`  
       `agent = harness(prompt = ROLES[role].prompt,`  
                       `tools  = ROLES[role].tools)`  
       `return agent.loop(task)`  
     
   **`run_copy`** starts `harness.py` again as a separate program. It is handed the system prompt and the tools of its role. `run_copy` waits for it, and returns only its final output.  
     
   `start_helpers(tasks):`  
       `helpers = [start_copy("helper", t) for t in tasks]`  
       `return [wait(h) for h in helpers]`  
     
   **`start_helpers`** is a tool the manager is given to spawn helper agents. The manager deploys helper agents in parallel, then waits for each to finish and returns their answers.  
     
   When the user invokes `/spawn <goal>`, the harness starts a new manager agent with the goal loaded in context. The manager can start new agent processes, each with its own context and tools, through the `start_helpers(tasks)` tool. The manager gives every helper its task at the same moment, then waits. Each helper works alone and sends back a report when it finishes. When the last report is in, the manager reads them all and writes one answer for you.  
     
   1. Add the /spawn command to harness.py. A spec file is provided in `upgrade_spec/SPAWN.md`. Review SPAWN.md and prompt an agent in VS Code chat to add the capabilities to your harness:

   

   `Read SPAWN.md found in upgrade_spec/SPAWN.md, and implement its spec into harness.py, following harness.py's structure. Ensure all tests in tests/test_multiagent.py pass.`

   

   2. Once built, `settings.json` should contain options relating to multi-agent orchestration, such as the maximum helpers the manager agent can spawn, the maximum minutes until a timeout, the maximum characters an agent takes in, and the models used.  
   3. Run `python tests/test_multiagent.py` from your harness folder to verify the agent correctly implemented multi-agent capabilities in your harness. It works by copying your harness into an empty temporary folder, typing /spawn into it, and reading what the run left behind: the files, the trace, and anything still running. It takes about a minute and prints `ok` when every check passes.

   

2. Use your harness to add new tools to harness.py using /spawn. A spec file in upgrade\_spec/TOOLS.md is provided. Below is a brief overview of the tools to be added:  
     
   * `fetch_url`: Returns a web page as plain text.  
   * `remember`: Saves a note in MEMORY.md, which the harness adds to every agent's context at the start of a run.  
   * `todo`: Keeps a task list in todo.md.  
   * `find_text`: Finds a string across the folder, with file and line.  
   * `undo`: Puts a file back the way it was before the last write.  
   * `diff`: Shows what the last write changed in a file.  
   * `cost`: Adds up the model calls, tokens and cost in trace.jsonl.  
   * `summarize`: Gives a file's content in a few lines.  
       
   1. Make a backup of harness.py, named harness.before.py. Then in settings.json, adjust `max_minutes` under spawn to 10, and check that `max_output_chars` under tools is at least 100000, or enough to read all of harness.py.  
        
   2. Open up the agent view GUI, then prompt your harness:  
        
      `/spawn implement the eight tools in upgrade_spec/TOOLS.md in harness.py. Start eight helpers at once, one tool each. Each helper writes only its own file, new_tools/<tool name>.py, holding that tool's function, and does not touch harness.py. When they have all reported, start one more helper to add every function to harness.py and to LOCAL_TOOLS, and to run each test in tests/ until it prints ok.`  
        
      While it runs, watch the agent view. Look for three things:  
        
      * How the manager split the job. Click its row and read the tasks it wrote.  
      * Whether the helpers' bars overlap. You should see eight bars stacked while the helpers each write their own file, then single bars while one helper at a time adds the tools to harness.py.  
      * What the manager does when a helper fails. It reads the report and sends a narrower task.

      

   3. A suite of tests is provided to verify each new tool's implementation, like `tests/test_fetch_url.py`. Your harness should have called these tests already, but they can be run by hand as a sanity check, like `python tests/test_fetch_url.py`.  
        
      **If a run goes wrong:** this is expected now and then, and nothing is lost. If harness.py will not start, put the backup back: copy harness.before.py over harness.py. If some tools are missing, run /spawn again and name only those: `/spawn add cost and summarize from new_tools/ to harness.py and to LOCAL_TOOLS, then run their tests in tests/ until they print ok.` Each run adds to what the last one finished.  
        
   4. \[OPTIONAL\] You may have noticed the prompt in 2 says "Each helper writes only its own file ... and does not touch harness.py." This is because parallel changes to one file collide, also known as a race condition. Make a separate copy of your harness folder and run the prompt again there, but only its first sentence. Observe how the manager delegates the task, and see whether it recognizes this collision.

   

2. A team of agents with no assigned roles scored a little higher than a single agent, at two to five times the cost. In this step, you'll find out whether assigning roles changes how well your team performs.  
     
   The job is to find out what went wrong when an imaginary ferry company's booking service went offline unexpectedly one afternoon. You're given `questions.md` to guide the team.  
     
   A job file gives the team a strategy for how to work. `job_1.md` says only what to answer and where to write the answers. `job_2.md` adds one paragraph: one question every incident raises for each helper, who owns which file, and what counts as done. You'll run both jobs, compare the two scores, and then write a third job of your own.  
     
   1. We will use a static simulated website. Open another terminal in p07/multiagent\_benchmark and start the page server.  
      `python3 serve.py`  
        
   2. Open the agent view. It should point to your harness session automatically.  
        
   3. Run the first job in your harness:  
        
      `/spawn Answer the questions in questions.md. Do the job in job_desc/job_1.md and write the answers to answers.jsonl.`  
        
      When it finishes, score it from a terminal in your harness folder:  
        
      `python tests/score_benchmark.py answers.jsonl`  
        
      It prints the score. Under it, from `trace.jsonl`, it prints the run's time, tokens, cost and tool use, with how often each tool worked. It saves a copy of the answers file in `p07/answers/`, with the time and the score in its name, so a later run never replaces it. It also adds one row for the run to `p07/answers/runs.md`, where your runs sit side by side.  
        
   4. Reset your harness's memory space, so the next run starts fresh. This deletes `MEMORY.md` and the answer files in your harness folder. The scored copy is already saved in `p07/answers/`, where no agent can read it.  
      `rm -f MEMORY.md && find . -maxdepth 1 -name 'answers*.jsonl' -delete`  
        
      > **What am I typing?**  
      > 

| What you type | What it means | From |
| :---- | :---- | :---- |
| `rm -f MEMORY.md` | Remove the notes the team saved with `remember`. | [man rm](https://man7.org/linux/man-pages/man1/rm.1.html) |
| `find . -maxdepth 1 -name 'answers*.jsonl' -delete` | Remove the answer files from this folder: `answers.jsonl` and each helper's own `answers-<name>.jsonl`. No other file is touched. | [man find](https://man7.org/linux/man-pages/man1/find.1.html) |
| `&&` | Run the next command only when the one before it worked. | [man bash](https://man7.org/linux/man-pages/man1/bash.1.html) |

      

   5. Run and score the second job the same way, with `job_2.md` in place of `job_1.md`. Then reset again with the same command.  
        
   6. Write your own job. Copy `job_desc/job_1.md` to a new file, `job_desc/job_3.md`, and add a paragraph on how the team works: who owns which pages, how many helpers start, and what counts as done. Say how the manager hands out the work, and what each helper does with its share. Your team can access the tools from step 2 if needed. If you are stuck, ask an AI chat for suggestions. Run the job and score it the same way.  
        
   7. You should now have three saved answers files in `p07_starter/p07/answers`, with `runs.md` beside them. Move the `answers` folder into your harness folder:  
      `mv ../p07/answers .`

## Turnin

Submit on the Project 7 assignment in Canvas, by Tuesday 11:59 pm:

* A zip file of your harness folder. Leave .env out of it.