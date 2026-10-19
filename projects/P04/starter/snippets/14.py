import random

def roll(times):
    results = []
    for _ in range(times):
        results.append(random.randint(1, 6))
    return results
