import os

def list_py(folder):
    names = os.listdir(folder)
    return [n for n in names if n.endswith(".py")]
