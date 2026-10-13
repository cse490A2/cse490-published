#!/usr/bin/env python3
"""The validation. Runs detector.is_phish over every email in the inbox and
prints the score: how many it got right, out of how many, beside the
target. Exits 0 when the score meets the target and 1 when it does not,
so an agent can read the result.

    python3 score.py                  # the public inbox, inbox.jsonl
    python3 score.py hidden.jsonl     # another inbox file (the staff's hidden set)

The target is the number to beat. The baseline detector does not reach it.
"""
import json, os, sys

TARGET = 54        # of 60: the number to beat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # detector.py lives beside this file, however python was started


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "inbox.jsonl"
    try:
        import detector
    except Exception as e:
        print("score: detector.py does not import: %s" % e)
        return 2
    emails = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    right, misses = 0, []
    for e in emails:
        answer = {k: v for k, v in e.items() if k != "phish"}
        try:
            guess = bool(detector.is_phish(answer))
        except Exception as ex:
            print("score: is_phish raised %s on %r" % (ex.__class__.__name__, e["subject"]))
            return 2
        if guess == e["phish"]:
            right += 1
        else:
            misses.append(("missed phish" if e["phish"] else "false alarm", e["subject"]))
    total = len(emails)
    target = TARGET if total == 60 else round(TARGET / 60 * total)
    for kind, subj in misses[:10]:
        print("  %-12s %s" % (kind, subj))
    if len(misses) > 10:
        print("  ... %d more" % (len(misses) - 10))
    print("score %d of %d  target %d of %d  %s" % (right, total, target, total, "PASS" if right >= target else "below target"))
    return 0 if right >= target else 1


if __name__ == "__main__":
    sys.exit(main())
