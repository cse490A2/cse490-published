import json

def save(settings, path):
    with open(path, "w") as f:
        json.dump(settings, f)
