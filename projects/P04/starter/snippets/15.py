def read_lines(path):
    try:
        with open(path) as f:
            return f.readlines()
    except FileNotFoundError:
        return []
