import sys

def main():
    if len(sys.argv) < 2:
        print("usage: count.py FILE")
        return 1
    with open(sys.argv[1]) as f:
        n = 0
        for line in f:
            n = n + 1
    print(n)
    return 0

sys.exit(main())
