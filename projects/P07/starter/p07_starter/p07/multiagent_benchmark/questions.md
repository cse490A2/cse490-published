# The Alder Point incident

Alder Point Ferries could not take bookings for part of Saturday 14 March 2026. The pages
served at http://localhost:8765/ are the company's records of that day: logs, the
monitoring export, the service's configurations, support tickets, the status page, a
postmortem draft and more. The index at / lists every page. The company and the incident
are invented for this project, so every answer has to come from the pages.

The records do not all agree. Some use UTC and some use local time. Some were written
from memory. Where two records disagree, the one made by a machine at the time is right.

Every question is about the one incident.
Submit one JSON line per question: {"n": 1, "answer": "...", "page": "filename.txt"}.
The page is the one the answer, or the last fact it needed, came from.

1. One configuration deploy went live shortly before the outage. How many settings did it change?
2. Which of those settings caused the outage? Write it as the new configuration does: name = value.
3. When did the first booking fail because of that setting? Answer in UTC as HH:MM:SS.
4. The first customer to tell the support desk about a failed booking quoted a booking id. When did that booking fail? Answer in UTC as HH:MM:SS.
5. The postmortem draft gives a start time for the outage. How many whole minutes later is it than the minute the first booking failed?
6. When did the fix take effect? Give the time the rollback completed, in UTC as HH:MM:SS.
7. How many bookings failed because of that setting, from the first failure to the fix?
8. Under the finance policy, how many dollars of travel credit does the company owe for them?
9. Who approved the change that caused the outage? Give the full name.
10. The company first blamed an outside company. By that company's own record, how many charge requests did it receive in the window it reports?
11. Last, the main question: what happened? In a few sentences, say what caused the outage, when it started and when it was fixed (UTC), how many bookings failed because of it, and who approved the change. Give this one as the answer of its line, with the page left empty.
