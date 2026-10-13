# Project 4 starter: the inbox

A stack of emails and a detector that is wrong too often. Your agent makes it right.

## The job

Make detector.py beat the target on inbox.jsonl without memorizing senders or subject lines. Run python3 score.py to see the score and the target. A second inbox you cannot see is scored the same way after you submit, so a detector that remembers these sixty emails loses there.

Send the job to your agent as a /plan message, for example:

    /plan make detector.py beat the target in score.py on inbox.jsonl without memorizing senders or subject lines

## What is here

| file | what it is |
|---|---|
| inbox.jsonl | sixty emails, one per line: from, subject, body, and phish, the answer |
| detector.py | the baseline detector, one keyword rule; is_phish(email) is the function the scorer calls |
| score.py | the validation: the score beside the target, exit 0 when it meets the target |
| skills/coding-loop/SKILL.md | the skill your agent follows: plan, approve, change, validation, report, transcript |

## The number to beat

    python3 score.py

prints the baseline's score and the target. The baseline is below it.
