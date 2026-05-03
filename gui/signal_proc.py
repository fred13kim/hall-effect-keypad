from collections import deque

class MovingAverage:
    def __init__(self, window_size=5):
        self.samples = deque(maxlen=window_size)

    def update(self, value):
        self.samples.append(value)
        return sum(self.samples) / len(self.samples)

    def reset(self):
        self.samples.clear()