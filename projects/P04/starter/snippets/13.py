def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

values = [fib(i) for i in range(10)]
