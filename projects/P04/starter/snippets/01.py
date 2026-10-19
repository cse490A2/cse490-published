def total(prices):
    result = 0
    for p in prices:
        result = result + p
    return result

print(total([3, 4, 5]))
