from typing import SupportsRound
from qns.schedular import Event, Simulator
from .entanglement import Entanglement


class GenerationEvent(Event):
    def __init__(self, link, init_time: float = None):
        super().__init__(init_time)
        self.link = link

    def run(self, simulator: Simulator):
        self.link.generation(simulator)


class GenerationEntanglementAfterEvent(Event):
    def __init__(self, e: Entanglement, link, nodes, init_time: float = None):
        super().__init__(init_time)
        self.link = link
        self.nodes = nodes
        self.e = e

    def run(self, simulator: Simulator):
        for n in self.nodes:
            if n.is_full():
                # print("generation failed due to memory limit")
                return
        for n in self.nodes:
            # e as message
            n.handle(simulator, self.e, source=self.link, event=self)
        # print(simulator.current_time,"generation successful")


class NodeSwappingEvent(Event):
    def __init__(self, e1: Entanglement, e2: Entanglement, node, source=None, init_time: float = None):
        super().__init__(init_time)
        self.node = node
        self.e1 = e1
        self.e2 = e2
        self.source = source

    def run(self, simulator: Simulator):
        self.node.handle(simulator, (self.e1, self.e2),
                         self.source, event=self)


class NodeSwappingAfterEvent(Event):
    def __init__(self, e: Entanglement, swap_node, target_nodes, init_time: float = None):
        super().__init__(init_time)
        self.target_nodes = target_nodes
        self.swap_node = swap_node
        self.e = e

    def run(self, simulator: Simulator):
        for n in self.target_nodes:
            if n.is_full():
                # print("generation failed due to memory limit")
                return
        for n in self.target_nodes:
            n.handle(simulator, self.e, source=self.swap_node, event=self)
        # print(simulator.current_time,"swapping successful")
