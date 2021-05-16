from qns.schedular import Protocol
from qns.schedular.simulator import Simulator, Event
from qns.topo import Node
from .entanglement import Entanglement
from .events import GenerationEntanglementAfterEvent, NodeSwappingAfterEvent, NodeSwappingEvent
import random

class QuantumNodeError(Exception):
    pass

class QuantumNodeGenerationProtocol(Protocol):
    def install(_self, simulator: Simulator):
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity
        if isinstance(event, GenerationEntanglementAfterEvent):
            e = msg
            self.add_entanglement(e)

class QuantumNodeSwappingProtocol(Protocol):
    def install(_self, simulator: Simulator):
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity
        # handle swapping
        if isinstance(event, NodeSwappingAfterEvent):
            e = msg
            self.add_entanglement(e)
        
        if self.route is None or len(self.route) < 2:
            return
        nodes1, nodes2 = self.route[0], self.route[1]
        e_set1, e_set2 = [],[]
        for e in self.registers:
            for n in e.nodes:
                if n == self:
                    continue
                if n in nodes1:
                    e_set1.append(e)
                if n in nodes2:
                    e_set2.append(e)


        map = zip(e_set1, e_set2)
        for e1, e2 in map:
            self.swapping(simulator, e1, e2)

class QuantumNode(Node):
    def __init__(self, registers_number: int = -1, swapping_func=None, distillation_func=None):
        self.links = []

        self.registers_number = registers_number
        self.registers: list(Entanglement) = []
        self.route = None

        if swapping_func is None:
            self.swapping_func = self.default_swapping_func
        else:
            self.swapping_func = swapping_func

        if distillation_func is None:
            self.distillation_func = self.default_distillation_func
        else:
            self.distillation_func = distillation_func

    # def install(self, simulator: Simulator):
    #     self.simulator = simulator

    # def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
    #     if isinstance(event, GenerationEntanglementAfterEvent):
    #         e = msg
    #         print("add generation entanglement", e)
    #         self.add_entanglement(e)

    #     # handle swapping
    #     if isinstance(event, NodeSwappingAfterEvent):
    #         e = msg
    #         print("add swapping entanglement", e)
    #         self.add_entanglement(e)
        
    #     if self.route is None or len(self.route) < 2:
    #         return
    #     nodes1, nodes2 = self.route[0], self.route[1]
    #     e_set1, e_set2 = [],[]
    #     for e in self.registers:
    #         for n in e.nodes:
    #             if n == self:
    #                 continue
    #             if n in nodes1:
    #                 e_set1.append(e)
    #             if n in nodes2:
    #                 e_set2.append(e)


    #     map = zip(e_set1, e_set2)
    #     for e1, e2 in map:
    #         self.swapping(simulator, e1, e2)

    def is_full(self):
        if self.registers_number != -1 and len(self.registers) >= self.registers_number:
            self.registers = [en for en in self.registers if en.is_alive()]
            return len(self.registers) >= self.registers_number
        return False

    def add_entanglement(self, e: Entanglement):
        if self.is_full():
            raise QuantumNodeError("out of quantum memory")
        self.registers.append(e)

    def remove_entanglement(self, e: Entanglement):
        self.registers.remove(e)

    def swapping(self, simulator: Simulator, e1: Entanglement, e2: Entanglement):
        self.swapping_func(simulator, e1, e2)

    def distillation(self, simulator: Simulator, e1: Entanglement, e2: Entanglement):
        self.distillation_func(simulator, e1, e2)

    def default_swapping_func(self, simulator: Simulator, e1: Entanglement, e2: Entanglement):
        swap_possible = 0.7
        swap_delay = 0.3
        swap_delay_time_slice = simulator.to_time_slice(swap_delay)
        node1 = None
        node2 = None
        for n in e1.nodes:
            if n is not self:
                node1 = n
                break
        for n in e2.nodes:
            if n is not self:
                node2 = n
                break
        if node1 is not None and node2 is not None:
            try:
                if e1 not in node1.registers and e2 not in node2.registers:
                    return
                node1.remove_entanglement(e1)
                node2.remove_entanglement(e2)
                self.remove_entanglement(e1)
                self.remove_entanglement(e2)
            except ValueError:
                return

            if random.random() > swap_possible:
                return
            f = 1/4 + 3/4 * (4 * e1.fidelity - 2) / 3 *  (4 * e2.fidelity - 2) / 3 
            ne = Entanglement([node1, node2], simulator.current_time_slice, f)
            nsae = NodeSwappingAfterEvent(ne, self, [node1, node2], simulator.current_time_slice)
            simulator.add_event(simulator.current_time_slice + swap_delay_time_slice, nsae)

    def default_distillation_func(self, simulator: Simulator, e1: Entanglement, e2: Entanglement):
        pass

class QuantumController(Node):
    def __init__(self, nodes):
        self.nodes = nodes

    def install(self, simulator: Simulator):
        self.simulator = simulator                                    
