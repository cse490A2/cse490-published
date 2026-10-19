def lengths(words):
    return {w: len(w) for w in words}

def longest(words):
    best = None
    for w in words:
        if best is None or len(w) > len(best):
            best = w
    return best
