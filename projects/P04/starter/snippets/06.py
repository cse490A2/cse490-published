class Counter:
    def __init__(self):
        self.count = 0

    def bump(self):
        self.count = self.count + 1
        return self.count
