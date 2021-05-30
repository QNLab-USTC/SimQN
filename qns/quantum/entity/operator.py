from qns.quantum.entity.channel import QuantumChannel
from qns.schedular import Entity
from qns.quantum.qubit import Polar, Qubit

class Generator(Entity):
    def __init__(self, delay: float = 0,name = None):
        '''
        Generator is a sub-entity in node. It can generate new qubit

        :param name: its name
        :param delay: its delay
        '''
        super().__init__(name)
        self.delay = delay
    
    def generate(self, polar: Polar) -> Qubit:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<generator {self.name}> "


class Measurer(Entity):
    def __init__(self):
        raise NotImplementedError


class Operator(Entity):
    def __init__(self):
        raise NotImplementedError