# CSE 490 A2: Vibe Coding

## Course facts

| Fact | Detail |
| :---- | :---- |
| Course | CSE 490 A2, Vibe Coding, UW Computer Science and Engineering |
| Credits | 2 |
| Meeting | Thursdays, 10:00-11:20 am, Savery Hall 220\. First meeting: Thursday, October 1 (2026-10-01) |
| Enrollment | 75 students, mostly seniors |
| Workload | 6 hours per week total, including lecture; most project work finishes in class, and the course keeps out-of-class work light |
| Instructor and office hours | To be announced before the first meeting |

## Overview

This course teaches the current, established techniques for building software with AI. Each week you build a working product in class with that week's toolkit: prompt-to-app platforms, coding assistants, CLI coding agents, multi-agent systems, local models, verification harnesses, and deployment pipelines. The course covers fundamentals such as how a large language model works, then spends most of its time on current tools and techniques; methods that are no longer state of the art receive no significant class time. AI runs through every part of the course itself: the curriculum and assignments are generated with AI, and projects are auto-graded.

## Schedule

| Id | Title | Topics |
| :---- | :---- | :---- |
| L01 | Prompt to App | Course overview; how an AI coding system works, from the invention of the LLM through completion IDEs to coding agents; how a prompt-to-app platform works, component by component; build and ship a first web app |
| L02 | The Prompt-Run-Refine Loop | Code generation versus agentic operation, the course's central distinction; prompting techniques for development work: specification prompts, decomposition, tests as targets; the prompt-run-refine loop as method; comparing models for a task and staying current in a churning field |
| L03 | AI in an Existing Codebase | Completions versus chat versus agent mode inside an IDE; feeding the assistant context; multi-file changes; keeping AI-assisted changes reviewable |
| L04 | Delegating to a Coding Agent | The agentic loop live: spec, plan, edit, run, fix; steering an agent when it drifts; agent configuration: instruction files, project memory, skills, personas; the Personal AI Dev Kit as an explicit habit |
| L05 | Multi-Agent Orchestration | Decomposition into planner, workers, and critic; named patterns: supervisor, fan-out, pipeline, debate; what multi-agent buys and what it costs |
| L06 | MCP and Agent Governance | Connecting third-party tools through MCP; context engineering: context windows, system prompts, memory; governance: permissions, allowlists, sandboxing, human-in-the-loop approval, audit trails |
| L07 | Local Models as Functions | Running models locally and the laptop sizing rule; structured outputs: the LLM as a typed function; local embeddings and semantic search; privacy, offline operation, and zero marginal cost, experienced live |
| L08 | Local Models in Real Time | Latency as the lesson: local event loops versus cloud round-trips; real-time MIDI generation with per-event intervention; local vision and speech-to-text as the same property in other senses; hearing a sampling distribution change under constraints |
| L09 | Verification and Evals | The trust gap in AI-generated code; reviewing, testing, and security-auditing AI output; designing evals that catch real failure modes; reading a generation trace, including how this course's auto-grader reads yours |
| L10 | Deploy Behind CI | The deploy-target landscape; CI with smoke tests: smoke subset per pull request, full suite on merge; recurring workflows as scheduled and triggered CI jobs; shipping an earlier project to production |

## Class format

Each 80-minute session splits roughly in half. The first half is lecture and live demo: the core topic, then the week's anchor tool demonstrated on a real build. The second half is in-class project work; you build that week's project with the same toolkit while the instructor and TAs answer individual questions. Projects are scoped to finish within the session, at about 40 minutes of build time. You may use out-of-class time to finish, and the course minimizes the need. Most weeks the project doubles as the homework; any short additional homework, such as week 1's video quiz, is announced in class.

## Tools and setup

The course uses several AI development tools across the quarter, deliberately: signing up for, configuring, and comparing tools is part of the skill set being taught. Each lecture has a pre-class setup checklist covering accounts, enrollments, and model downloads, sent ahead of the session; a consolidated week-1 checklist, announced in the first lecture, front-loads as much of this as possible. Please complete each checklist before class. Classroom Wi-Fi cannot be relied on, so anything downloadable is downloaded at home. The current tool list, enrollment steps, and verified costs live in the setup checklists. Total out-of-pocket cost stays under 100 dollars for the quarter; most weeks ride free tiers.

## Grading

| Component | Weight |
| :---- | :---- |
| Weekly projects L01-L10, equally weighted, lowest score dropped | 85% |
| Participation | 10% |
| Lightning demo | 5% |

Projects are auto-graded. Each project carries a standard rubric implemented by analyzing the code or the program generation trace, so grading is fair, reliable, and repeatable: two students who do similar work receive about the same grade. The done-conditions on each project sheet are the pass/fail checks, run against the deliverable itself; the generation trace you submit is the evidence for the remainder. The lowest-score drop covers L10 like any other week. The percentage-to-4.0 mapping is deterministic and is published before the first project is graded. If you believe a grade is wrong, please email the course staff within one week of the grade posting.

## Per-lecture feedback

After each lecture you say what worked and what did not, through a short feedback form. That feedback enters a versioned intake and drives revision within the quarter, so later lectures improve while you are still in the course. Each offering improves on the last the same way.

## Religious accommodations

Washington state law requires that UW develop a policy for accommodation of student absences or significant hardship due to reasons of faith or conscience, or for organized religious activities. The UW's policy, including more information about how to request an accommodation, is available at Religious Accommodations Policy ([https://registrar.washington.edu/staffandfaculty/religious-accommodations-policy/](https://registrar.washington.edu/staffandfaculty/religious-accommodations-policy/)). Accommodations must be requested within the first two weeks of this course using the Religious Accommodations Request form ([https://registrar.washington.edu/students/religious-accommodations-request/](https://registrar.washington.edu/students/religious-accommodations-request/)).

## Access and accommodations

It is the policy and practice of the University of Washington to create inclusive and accessible learning environments consistent with federal and state law. If you have already established accommodations with Disability Resources for Students (DRS), please activate your accommodations so we can discuss how they will be implemented in this course. If you have a temporary health condition or a permanent disability that requires accommodations and you have not yet established services through DRS, please contact DRS directly: disability.uw.edu, 206-543-8924, [uwdrs@uw.edu](mailto:uwdrs@uw.edu). DRS offers resources and coordinates reasonable accommodations for students with disabilities and temporary health conditions.

## Academic integrity and AI use

This course requires AI use in every assignment, so integrity here means honest representation of the work. Submit only work whose generation you can account for. The generation trace you submit is the record of what you asked and what the AI produced, and grading reads it. Misrepresenting a trace, submitting another person's work or trace as your own, or fabricating results is academic misconduct. The course is governed by the UW Student Conduct Code, WAC 478-121 ([https://app.leg.wa.gov/wac/default.aspx?cite=478-121](https://app.leg.wa.gov/wac/default.aspx?cite=478-121)), and the Allen School academic misconduct policy ([https://www.cs.washington.edu/academics/schoolwide-policies/](https://www.cs.washington.edu/academics/schoolwide-policies/)); suspected violations are referred to Community Standards and Student Conduct.

The course requires accounts with several third-party AI services, and no UW data-protection agreement covers them. Do not paste private data, or other people's personal data, into third-party AI tools. If you are unsure whether a particular use of AI is allowed on an assignment, ask the course staff before submitting.

## Safety

Call SafeCampus at 206-685-7233 anytime, no matter where you work or study, to anonymously discuss safety and well-being concerns for yourself or others. More information: safecampus.uw.edu.

# Why this syllabus

Why this schedule, in this order, under these constraints. Instructor-facing; the student syllabus states the what, this file states the why.

## The ordering logic

The quarter runs from the shortest possible distance to a shipped product toward shipping with production discipline. L01 starts at prompt-to-app because it gives every student a working artifact in week one with no environment setup beyond a browser account, and because the first session must also carry the course overview. A win in the first 80 minutes sets the tone for a class whose whole premise is that AI collapses the distance from intent to software.

L02 opens the course's central distinction, code generation versus agentic operation, and installs the working method: prompt, run, read the failure, refine, with tests as the target. L04 completes that distinction by putting a CLI agent on the other side of it. L03 sits between them because most industry AI work happens inside code someone else wrote; it also gives students the assistant-in-IDE experience before they hand the whole loop to an agent. The progression is deliberate: watch the model complete your line, then converse with it about a repo, then delegate the repo to it.

L04 through L06 are the agent arc: one agent, many agents, then connected and governed agents. Governance shares L06 with MCP rather than taking its own week. That is a real trade, discussed below. It is also a defensible lesson design: granting an agent tool access and constraining that access are two halves of one skill. Teaching them apart invites students to learn capability without control.

L07 and L08 are the local-model weeks. They land after the agent arc on purpose. By week seven students have spent six weeks paying for cloud round-trips with latency, rate limits, and quota anxiety, so the local propositions land experientially instead of as claims. Privacy is extraction from records you would never post. Offline is the Wi-Fi kill mid-demo. Cost is pricing the session at API rates against zero. The functions week precedes the real-time week because structured extraction carries zero hardware risk across 75 mixed laptops and teaches the deepest transferable concept, the LLM as a typed function. Real-time work builds on the serving confidence from the week before.

L09 comes late because verification needs a quarter of AI-generated code to have opinions about. It is also the highest-resume-weight week in the course. The industry research shows adoption near universal at about 84 percent while almost nobody highly trusts the output, about 3 percent. The top practitioner frustration is solutions that are almost right. Placing evals directly before deployment means the verification habit ships with the final project rather than being an epilogue.

L10 closes with deployment behind CI, and the student ships an earlier project of their choosing. The compounding toolkit pays off visibly in the last session: something built weeks ago goes to production behind a green build.

## How the schedule honors the constraints

The 2-credit budget is the binding constraint. Every project is scoped to about 40 minutes of in-class build time for a senior with no special domain expertise. Setup is exiled to pre-class checklists, with a consolidated week-1 checklist front-loading the bulk. Homework beyond the projects is nearly nil: one video quiz in week one. When scope and ambition conflicted, scope lost.

The local-model requirement asked for at least one week and ideally two. The research split, functions then real time, fills two cleanly and gives each week its own lesson rather than stretching one lesson across two sessions.

The must-have curriculum is covered: the objective-by-objective table in the course specification shows every instructor objective O1 through O12 served by at least one lecture, with the derived objectives D1 through D6 carried as secondary targets. Nothing on the instructor's list depends on a week that does not exist.

Compounding is structural, with no single quarter-long build. Dev Kit entries accrue at L02 (prompt patterns and the test-first habit), L04 (the agent configuration), L06 (the MCP configuration), and L09 (the eval suite), and L10 spends them by shipping an earlier project. The research supports this shape: a portfolio of standalone builds plus a reusable tool repo reads stronger to hiring managers than a single culminating artifact.

## What was traded off

Governance lost its dedicated week; it shares L06 with MCP. The freed slot funds the second local week. The bet is that capability-plus-control as one lesson teaches better than control alone a week later, but it does compress a topic the objectives care about.

Skills, personas, and recurring workflows became supporting topics inside L04 and L10 rather than dedicated coverage. They are taught and exercised, not spotlighted.

L07's in-class project is schema-constrained extraction rather than the voice pipeline. The voice pipeline is the better demo moment and keeps that role, Wi-Fi kill included; the extraction build is the zero-hardware-risk pick for 75 mixed laptops, many without GPUs.

L01 is sized for deliberate prompting because every builder on the student-choice menu holds its free tier to a handful of build interactions per day. The alternative was funding week-one credits; deliberate prompting was judged the better lesson and the cheaper one.

No single quarter-long build exists anywhere in the schedule; the owner removed it. Every project stands alone, and the Dev Kit carries the compounding such a thread would have.

## Open items bearing on this syllabus

The grading split of 85/10/5 follows the owner's hint and awaits confirmation on a review doc. Lightning-demo mechanics are undefined. Instructor contact and office hours are absent from the sources, so the syllabus says "to be announced"; the compliance audit flags the same gap. The budget mechanism under the 100-dollar cap remains unset. The full list lives in the open-questions section of the course specification.