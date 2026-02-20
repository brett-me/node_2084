class Suspicion:
    """tracks suspicion (0 - 100) and simulates integrity effects"""

    def __init__(self):
        self.value = 0

    def increase(self, amount):
        self.value += amount
        if self.value > 100:
            self.value = 100

    def decrease(self, amount):
        self.value -= amount
        if self.value < 0:
            self.value = 0

    def update(self, dt):
        pass
