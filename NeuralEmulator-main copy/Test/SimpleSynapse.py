from NeuralEmulator.Interfaces.CurrentSourceBase import CurrentSourceBase


class SimpleSynapse(CurrentSourceBase):
    def __init__(self, currentVal=0):
        self.current = currentVal

    def getCurrent(self):
        return self.current

    def setCurrent(self, current):
        self.current = current

    def run(self):
        pass


if __name__ == "__main__":
    b = SimpleSynapse()
    val = b.getCurrent()
    print(val)
