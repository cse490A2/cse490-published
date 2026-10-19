import csv

def load(path):
    rows = []
    with open(path) as f:
        for row in csv.reader(f):
            rows.append(row)
    return rows
