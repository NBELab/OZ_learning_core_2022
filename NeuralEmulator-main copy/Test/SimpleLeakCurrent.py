from NeuralEmulator.Interfaces.CurrentSourceBase import CurrentSourceBase


class SimpleLeakCurrent(CurrentSourceBase):
    def __init__(self, current):
        self.current = current

    def getCurrent(self):
        return self.current

    def setCurrent(self, val):
        self.current = val

    def run(self):
        pass
