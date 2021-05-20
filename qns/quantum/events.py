from qns.schedular.entity import Entity
from typing import SupportsRound
from qns.schedular import Event, Simulator
from .entanglement import Entanglement
from qns.log import log


class GenerationAllocateEvent(Event):
    def __init__(self, protocol, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol

    def run(self, simulator: Simulator):
        self.protocol.allocate(simulator)


class GenerationEvent(Event):
    def __init__(self, protocol, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol

    def run(self, simulator: Simulator):
        self.protocol.generation(simulator)


class GenerationEntanglementAfterEvent(Event):
    def __init__(self, e: Entanglement, link, nodes, init_time: float = None):
        super().__init__(init_time)
        self.link = link
        self.nodes = nodes
        self.e = e

    def run(self, simulator: Simulator):
        for n in self.nodes:
            if n.is_full():
                log.debug("generate {} failed due to memory limit", self.e)
                return
        for n in self.nodes:
            # e as message
            n.add_entanglement(self.e)
            n.call(simulator, self.e, self.link, self)
        log.debug("generate {} successful", self.e)
        # print(simulator.current_time,"generation successful")


class NodeSwappingEvent(Event):
    def __init__(self, protocol,  e1: Entanglement, e2: Entanglement, source=None, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol
        self.e1 = e1
        self.e2 = e2
        self.source = source

    def run(self, simulator: Simulator):
        # self.node.call(simulator, (self.e1, self.e2),
        #  self.source, event=self)
        self.protocol.swapping(simulator, self.e1, self.e2)


class NodeSwappingAfterEvent(Event):
    def __init__(self, node, init_time: float = None):
        super().__init__(init_time)
        self.node = node

    def run(self, simulator: Simulator):
        pass


class NodeDistillationEvent(Event):
    def __init__(self, protocol, e1: Entanglement, e2: Entanglement, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol
        self.e1 = e1
        self.e2 = e2

    def run(self, simulator: Simulator):
        self.protocol.distillation(simulator, self.e1, self.e2)


class NodeDistillationAfterEvent(Event):
    def __init__(self, node, init_time: float = None):
        super().__init__(init_time)
        self.node = node

    def run(self, simulator: Simulator):
        pass
