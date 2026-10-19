def average(scores):
    if len(scores) == 0:
        return None
    return sum(scores) / len(scores)

grades = {"ada": [90, 95], "bob": [70]}
for name, marks in grades.items():
    print(name, average(marks))
