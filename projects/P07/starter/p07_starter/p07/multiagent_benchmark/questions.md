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

Two questions have parts (a) to (d), and each needs several pages. Submit one of those as
{"n": 11, "answer": {"a": "...", "b": "...", "c": "...", "d": "..."}, "pages": ["file.txt", "..."]}.
Name every page the answer needed. A list in a part is separated by commas, in any order.

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
11. The release policy has five numbered rules, and the runbook sets a floor for the database pool. Judge the deploy that caused the outage against them. (a) Which of the five rules did it not follow? Give the rule numbers. (b) Which settings did it change that its summary did not list? Give the names only. (c) How many whole minutes before the sailing release opened did it go live? (d) By how many connections was its pool under the runbook's floor?
12. Follow the customers, not the bookings. Take the customers who had a booking fail because of that setting. (a) How many of them completed a booking later that day, after their first failure? (b) How many never did, by the end of the booking log? (c) How many dollars of the travel credit go to the customers in (a), who got a ticket anyway? (d) What fare did the company lose from the customers in (b)? Count each one's first failed booking: the adult fare of its route times its passengers. Answer in dollars.
13. Last, the main question: what happened? In a few sentences, say what caused the outage, when it started and when it was fixed (UTC), how many bookings failed because of it, and who approved the change. Give this one as the answer of its line, with the page left empty.
