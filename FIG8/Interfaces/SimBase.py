from abc import ABC, abstractmethod


class SimBase(ABC):
    @abstractmethod
    def run(self):
        pass
