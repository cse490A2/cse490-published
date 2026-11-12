---
title: "P07: A Team Upgrades Your Agent"
parent: "Projects"
nav_order: 7
has_children: true
permalink: "/projects/P07/"
---

# Project 7: A Team Upgrades Your Agent

**Due: Tuesday 11:59 pm**  
Prerequisites: finish the setup guide first. You have a harness that writes trace.jsonl, the Project 7 starter files, and the agent view open in your browser.  
In this project, you add a team to your harness. One command, /spawn, starts a manager agent. The manager splits a goal into tasks and starts one helper agent per task, all at once. You use the team to build eight new tools, and then you measure how well it answers a set of questions.

Use external/haiku-5-5 for every agent. Off campus, connect the UW VPN first.

## Instructions

1. So far your harness has been one agent. We'll now add the ability to spawn several agents from one harness session. A team of agents can split a job into pieces and work on them at the same moment. This is useful to divide and conquer a task without you managing several agents yourself.  
     
   Let's consider an example of the proposed interface, `/spawn <goal>`:  
     
   `/spawn find why the gifv tests fail, edit only thumbor/engines/, and report the failing line with its error.`  
     
   /spawn is a command you type; the model cannot call it by itself. In this example, the user is asking for a complex task: fixing a bug. For this assignment, we'll create a manager-helper style of orchestration. When /spawn is invoked, a manager is handed the goal and is responsible for delegating to helper agents. We can define the general behavior and strategy of agent deployment, or leave it up to the model to decide. We control how many helpers one call may start with a limit in settings.json.  
     
   Here's roughly how our orchestration will work:  
     
   `spawn(goal):                    # you type /spawn`  
       `report = run_copy("manager", goal)`  
       `print(report)`  
   `run_copy(role, task):           # a new process`  
       `agent = harness(prompt = ROLES[role].prompt,`  
                       `tools  = ROLES[role].tools)`  
       `return agent.loop(task)     # its last reply`  
   `start_helpers(tasks):           # the manager's tool`  
       `helpers = [start_copy("helper", t)`  
                  `for t in tasks]          # all at once`  
       `return [wait(h) for h in helpers]   # the reports`  
     
   When the user invokes `/spawn <goal>`, the harness starts a new manager agent with the goal loaded in context. The manager can start new agent processes, each with its own context and tools, through the `start_helpers(tasks)` tool. run\_copy starts a copy and waits for it. start\_copy starts one and returns at once, which is how the helpers run at the same moment. Once all helpers are finished and have reported back to the manager, the manager reports to the user.  
     
   1. Add the /spawn command to harness.py. A spec file is provided in upgrade\_spec/SPAWN.md. It describes what the command does, what a manager and a helper are, and the limits a run stops at. Review SPAWN.md and prompt an agent in VS Code chat to add the capabilities to your harness.  
   2. Once built, settings.json should contain options relating to multi-agent orchestration, such as the maximum helpers the manager agent can spawn, the maximum minutes until a timeout, and the model types.  
   3. Run `python tests/test_multiagent.py` from your harness folder to verify the agent correctly implemented multi-agent capabilities in your harness. It works by copying your harness into an empty temporary folder, typing /spawn into it, and reading what the run left behind: the files, the trace, and anything still running. It takes about a minute and prints `ok` when every check passes. SPAWN.md lists the checks.

   

2. Use your harness to add new tools to harness.py using /spawn. A spec file in upgrade\_spec/TOOLS.md is provided. Below is a brief overview of the tools to be added:  
     
   * `fetch_url`: Returns a web page as plain text.  
   * `remember`: Introduces MEMORY.md for agents to write in.  
   * `todo`: Agents will manage a task list in todo.md.  
   * `find_text`: Finds a string across the folder, with file and line.  
   * `undo`: Puts a file back the way it was before the last write.  
   * `diff`: Shows what the last write changed in a file.  
   * `cost`: Adds up the model calls, tokens and cost in trace.jsonl.  
   * `summarize`: Gives a file's content in a few lines.  
       
   1. Make a backup of harness.py, named harness.before.py. Then in settings.json, adjust `max_minutes` under spawn to 10, and check that `max_output_chars` under tools is at least 60000, so a helper can read all of harness.py.  
        
   2. Set up agent view, and prompt your harness:  
        
      `/spawn implement the eight tools in upgrade_spec/TOOLS.md in harness.py. Start eight helpers at once, one tool each. Each helper writes only its own file, new_tools/<tool name>.py, holding that tool's function, and does not touch harness.py. When they have all reported, start one more helper to add every function to harness.py and to LOCAL_TOOLS, and to run each test in tests/ until it prints ok.`  
        
      While it runs, watch the agent view. Look for three things:  
        
      * How the manager split the job. Click its row and read the tasks it wrote.  
      * Whether the helpers' bars overlap. You should see eight bars stacked while the helpers each write their own file, then single bars while one helper at a time adds the tools to harness.py.  
      * What the manager does when a helper fails. It reads the report and sends a narrower task.

      

   3. A suite of tests is provided to verify each new tool's implementation, like `tests/test_fetch_url.py`. Your harness should have called these tests already, but they can be run by hand as a sanity check: `python tests/test_fetch_url.py`. A tool is done when its test prints ok.  
        
   4. When the run finishes, Take a screenshot of your agent view window.  
        
      **If a run goes wrong:** this is expected now and then, and nothing is lost. If harness.py will not start, put the backup back: copy harness.before.py over harness.py. If some tools are missing, run /spawn again and name only those: `/spawn add cost and summarize from new_tools/ to harness.py and to LOCAL_TOOLS, then run their tests in tests/ until they print ok.` Each run adds to what the last one finished.  
        
   5. \[OPTIONAL\] You may have noticed the prompt in 2 says "Each helper writes only its own file ... and does not touch harness.py." This is because parallel changes to one file collide, also known as a race condition. Make a separate copy of your harness folder and run the prompt again there, but only its first sentence. Observe how the manager delegates the task, and see if it recognizes this collision.

   

2. questions.md asks eleven questions about one invented incident: a ferry company's booking service went down for an afternoon. The answers are spread over 85 pages of the company's records, and the records do not all agree.  
     
   A job file tells the team how to work. job\_desc holds two. job\_1.md says only what to answer and where to write it. job\_2.md says the same, and adds a strategy: which helper owns which pages, what each one writes, and what done means. You'll run both, score both, and then write a strategy of your own.  
     
   1. We will use a static simulated website. Open another terminal in p07/multiagent\_benchmark and start the page server. `python3 serve.py`  
        
   2. In settings.json, set `max_minutes` under spawn back to 10\.  
        
   3. With the agent view open, run the first job in your harness:  
        
      `/spawn Answer questions in questinos.md. Do the job in job_desc/job_1.md and write the answers to answers_1.jsonl.`  
        
      When it finishes, score it from a terminal in your harness folder:  
        
      `python tests/score_benchmark.py answers_1.jsonl`  
        
   4. Clear what that run left behind, so the next one starts fresh:  
      `rm -f answers-*.jsonl MEMORY.md`  
        
      Then run and score the second job the same way, with job\_2.md and answers\_2.jsonl.  
        
   5. Compare the two runs. Look at the score, the minutes and cost in the agent view, and the shape of the bars.  
        
   6. Write your own strategy. Copy job\_desc/job\_1.md to job\_desc/job\_3.md and add your own paragraph on how the team works. Decide who owns which pages, how many helpers start, which questions need another question's answer first, and what done means. Use what you saw in sub-step 5\. Clear the folder again, run it with answers\_3.jsonl, and score it. Try to beat both.

## Turnin

Submit on the Project 7 assignment in Canvas, by Tuesday 11:59 pm:

* A zip file of your harness folder. Leave .env out of it.  
* A screenshot of the agent view during step 2\.  
* A screenshot of the three scores from step 3\.  
* Your job\_desc/job\_3.md. It is in the zip already if you saved it in your harness folder.