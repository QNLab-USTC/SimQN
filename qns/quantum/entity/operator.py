from qns.quantum.entity.channel import QuantumChannel
from qns.schedular import Entity, Simulator, Event
from qns.quantum.qubit import Polar, Qubit

class Generator(Entity):
    def __init__(self, delay: float = 0, fidelity = 1,name = None):
        '''
        Generator is a sub-entity in node. It can generate new qubit

        :param name: its name
        :param delay: its delay
        '''
        super().__init__(name)
        self.delay = delay
        self.fidelity = fidelity
    
    def install(self, simulator: Simulator):
        self.simulator = simulator

    
    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        '''
        
        '''
        pass
    
    def generate(self, polar: Polar) -> Qubit:
        '''
        Generate a new qubit with certain fidelity and polar

        :param: the polarization of this qubit
        :returns: the newly generated qubit
        '''
        e = Qubit(self.simulator.current_time_slice, fidelity = self.fidelity, live_func = None)
        e.set_polar(polar)
        return e

    def __repr__(self) -> str:
        return f"<generator {self.name}> "


class Measurer(Entity):
    def __init__(self):
        raise NotImplementedError


class Operator(Entity):
    def __init__(self):
        raise NotImplementedError