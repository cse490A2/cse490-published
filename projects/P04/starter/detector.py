#!/usr/bin/env python3
"""The phishing detector. is_phish(email) says whether one email is a phish.
This is the baseline the starter ships: one rule, so it is wrong often.
Your agent improves it. The scorer imports this file; keep the function's
name and shape.

An email is a dict: from, subject, body (strings) and, in the inbox file,
phish (the answer, which the detector never reads).
"""
import json, sys

URGENT = ("urgent", "password", "suspended", "verify")


def is_phish(email):
    """True when the email looks like a phish."""
    text = (email["subject"] + " " + email["body"]).lower()
    return any(w in text for w in URGENT)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "inbox.jsonl"
    for line in open(path, encoding="utf-8"):
        e = json.loads(line)
        print("PHISH " if is_phish(e) else "ok    ", e["subject"])
