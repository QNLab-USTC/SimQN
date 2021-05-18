
import random
from qns.quantum.entanglement import Entanglement
from qns.topo import Channel
from qns.schedular import Simulator, Event, Protocol
from .events import GenerationAllocateEvent, GenerationEntanglementAfterEvent, GenerationEvent
from qns.log import log


class QuantumChannel(Channel):
    def __init__(self, nodes=[],  name=None):
        self.nodes = nodes

        if name is None:
            self.name = str(id(self))
        else:
            self.name = name

    def __repr__(self):
        return "<link " + self.name+">"

class GenerationProtocal(Protocol):

    def __init__(_self, entity, possible = 1, rate = 10, delay = 0.02, fidelity = 1, allocate_step = 1):
        super().__init__(entity)
        _self.possible = possible
        _self.delay = delay
        _self.fidelity = fidelity
        _self.rate = rate
        _self.step = allocate_step

    def install(_self, simulator: Simulator):
        self = _self.entity
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

        for n in self.nodes:
            n.links.append(self)

        # ge = GenerationEvent(_self, simulator.current_time)
        gae = GenerationAllocateEvent(_self, simulator.current_time)
        start_time_slice = simulator.start_time_slice
        end_time_slice = simulator.end_time_slice
        # step_time_slice = int(simulator.time_accuracy / _self.rate)
        _self.allocate_step_time_slice = simulator.to_time_slice(_self.step)
        for t in range(start_time_slice, end_time_slice, _self.allocate_step_time_slice):
            simulator.add_event(t, gae)

    def allocate(_self, simulator: Simulator):
        self = _self.entity
        log.debug(f"link {self} begin allocate")

        ge = GenerationEvent(_self, simulator.current_time)

        start_time_slice = simulator.current_time_slice
        end_time_slice = simulator.current_time_slice + _self.allocate_step_time_slice
        step_time_slice = int(simulator.time_accuracy / _self.rate)
        for t in range(start_time_slice, end_time_slice, step_time_slice):
            simulator.add_event(t, ge)

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        pass
    
    def generation(_self, simulator: Simulator):
        self = _self.entity

        if random.random() > _self.possible:
            log.debug("{} generation failed".format(self))
            return

        e = Entanglement(self.nodes, simulator.current_time_slice, fidelity= _self.fidelity)
        geae = GenerationEntanglementAfterEvent(
            e, self, self.nodes, simulator.current_time)
        simulator.add_event(simulator.current_time_slice +
                            _self.delay_time_slice, geae)