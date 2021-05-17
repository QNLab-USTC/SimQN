from qns.schedular import Protocol
from qns.schedular.simulator import Simulator, Event
from qns.topo import Node
from .entanglement import Entanglement
from .events import NodeDistillationAfterEvent, NodeDistillationEvent, NodeSwappingAfterEvent,  NodeSwappingEvent
from qns.log import log
import random


class QuantumNodeError(Exception):
    pass


class QuantumNode(Node):
    def __init__(self, registers_number: int = -1, name=None):
        self.links = []

        self.registers_number = registers_number
        self.registers: list(Entanglement) = []
        self.route = None
        if name is None:
            self.name = str(id(self))
        else:
            self.name = name

    def is_full(self):
        if self.registers_number != -1 and len(self.registers) >= self.registers_number:
            self.registers = [en for en in self.registers if en.is_alive()]
            return len(self.registers) >= self.registers_number
        return False

    def add_entanglement(self, e: Entanglement):
        if self.is_full():
            raise QuantumNodeError("out of quantum memory")
        self.registers.insert(0, e)

    def remove_entanglement(self, e: Entanglement):
        self.registers.remove(e)

    def __repr__(self):
        return "<node " + self.name+">"

class QuantumNodeGenerationProtocol(Protocol):
    def install(_self, simulator: Simulator):
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity
        pass


class QuantumNodeSwappingProtocol(Protocol):
    def __init__(_self, entity, possible=1, delay=0, fidelity_func=None, under_controlled = False):
        _self.entity = entity
        _self.entity.router = []
        _self.possible = possible
        _self.delay = delay
        _self.fidelity_func = fidelity_func
        _self.under_controlled = under_controlled

    def install(_self, simulator: Simulator):
        _self.entity.router = []
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity
        if _self.under_controlled:
            return

        if self.route is None or len(self.route) < 2:
            return
        nodes1, nodes2 = self.route[0], self.route[1]
        e_set1, e_set2 = [], []
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
            log.debug("swap start using {} and {}", e1, e2)
            swapevent = NodeSwappingEvent(_self, e1, e2)
            simulator.add_event(simulator.current_time_slice +
                                _self.delay_time_slice, swapevent)

    def swapping(_self, simulator: Simulator, e1: Entanglement, e2: Entanglement):
        self = _self.entity

        node1 = None
        node2 = None

        for n in e1.nodes:
            if e1 in n.registers:
                n.remove_entanglement(e1)
            if n is not self:
                node1 = n
                break
        for n in e2.nodes:
            if e2 in n.registers:
                n.remove_entanglement(e2)
            if n is not self:
                node2 = n
                break

        if node1 is None or node2 is None:
            log.debug("break swapping between {} and {}", e1, e2)

        if random.random() > _self.possible:
            log.debug("swapping between {} and {} failed", e1, e2)
            return

        f = _self.fidelity(e1, e2)
        nodes = [node1, node2]
        ne = Entanglement(nodes, simulator.current_time_slice, f)

        for n in nodes:
            if n.is_full():
                log.debug("swapping break between {} and {}", e1, e2)
                return
        for n in nodes:
            n.add_entanglement(ne)
            nsae = NodeSwappingAfterEvent(simulator.current_time)
            n.call(simulator, ne, self, nsae)

        log.debug("swap success to generate {} using {} and {} ", ne, e1, e2)

    def fidelity(_self, e1, e2):
        if _self.fidelity_func is not None:
            return _self.fidelity_func(e1, e2)
        return e1.fidelity * e2.fidelity
        # return 1/4 + 3/4 * (4 * e1.fidelity - 2) / 3 * (4 * e2.fidelity - 2) / 3


class QuantumNodeDistillationProtocol(Protocol):
    def __init__(_self, entity: QuantumNode, threshold: float = 0, delay: float = 0, under_controlled = False):
        super().__init__(entity)
        _self.threshold = threshold
        _self.delay = delay
        _self.under_controlled = under_controlled

    def install(_self, simulator: Simulator):
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)
        _self.entity.allow_distillation = []

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity  # self is a QuantumNode

        if _self.under_controlled:
            return

        need_distillation = {}

        for e in self.registers:
            for n in e.nodes:
                if n == self:
                    continue
                if n in self.allow_distillation and e.fidelity <= _self.threshold:
                    if n in need_distillation.keys():
                        need_distillation[n].append(e)
                    else:
                        need_distillation[n] = [e]
        map = []
        for es in need_distillation.values():
            ll = len(es) // 2
            map += [(es[2*i], es[2*i + 1]) for i in range(ll)]

        for (e1, e2) in map:
            log.debug("distillation start on {} using {} and {}", self, e1, e2)
            ede = NodeDistillationEvent(_self, e1, e2)
            simulator.add_event(
                simulator.current_time_slice + _self.delay_time_slice, ede)

    def distillation(self, simulator: Simulator, e1, e2):

        for n in e1.nodes:
            if n not in e2.nodes:
                log.warn("{} and {} can not used for distillation", e1, e2)
                return

        f_min = min(e1.fidelity, e2.fidelity)
        f = f_min**2 / (f_min**2 + (1-f_min)**2)
        poss = f_min**2 + (1-f_min)**2

        for n in e1.nodes:
            if e1 not in n.registers or e2 not in n.registers:
                log.warn("{} or {} is not in {}", e1, e2, n)
                return
            n.remove_entanglement(e1)
            n.remove_entanglement(e2)

        if random.random() > poss:
            log.warn("{} and {} distillation failure: {}", e1, e2, poss)
            return

        ne = Entanglement(e1.nodes, simulator.current_time, fidelity=f)
        for n in ne.nodes:
            if n.is_full():
                log.warn(
                    "{} and {} distillation failure due to {} is full", e1, e2, n)
                return
        for n in ne.nodes:
            n.add_entanglement(ne)
            ndae = NodeDistillationAfterEvent(simulator.current_time)
            n.call(simulator, ne, self, ndae)
        log.debug("{} distillation successfully", ne)
