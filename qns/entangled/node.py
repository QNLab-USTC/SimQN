from qns.bb84 import fiber
from qns.schedular import Protocol
from qns.schedular.simulator import Simulator, Event
from qns.topo import Node
from .entanglement import Entanglement
from .events import NodeDistillationAfterEvent, NodeDistillationEvent, NodeSwappingAfterEvent,  NodeSwappingEvent
from qns.log import log
import random


class QuantumNodeError(Exception):
    '''
    An error occured on a ``QuantumNode``.
    '''
    pass


class QuantumNode(Node):
    '''
    A quantum node in entanglement based network model

    :param registers_number: the size of its quantum memory, ``-1`` means unlimited.
    :param name: its name
    :var registers: its quantum registers (or memory)
    '''

    def __init__(self, registers_number: int = -1, name=None):
        super().__init__(name)
        self.links = []

        self.registers_number = registers_number
        self.registers: list(Entanglement) = []
        self.swapping_schema = None

    def is_full(self):
        '''
        To check whether its registers is all used or not

        :returns bool: whether its reigsters is full
        '''
        if self.registers_number != -1 and len(self.registers) >= self.registers_number:
            self.registers = [en for en in self.registers if en.is_alive()]
            return len(self.registers) >= self.registers_number
        return False

    def add_entanglement(self, e: Entanglement):
        '''
        add an entanglement into registers:

        :param Entanglement e: the new coming entangled qubit
        :raises QuantumNodeError: The registers is full
        '''
        if self.is_full():
            raise QuantumNodeError("out of quantum memory")
        self.registers.insert(0, e)

    def remove_entanglement(self, e: Entanglement):
        '''
        remove an entanglement from registers:

        :param Entanglement e: the removing entangled qubit
        '''
        self.registers.remove(e)

    def __repr__(self):
        return "<node " + self.name+">"


class QuantumNodeGenerationProtocol(Protocol):
    '''
    This is the entanglement generation protocol

    .. warning::
        It is now deprecated
    '''
    def install(_self, simulator: Simulator):
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity
        pass


class QuantumNodeSwappingProtocol(Protocol):
    '''
    This is the swapping protocol for ``QuantumNode`` .

    If ``under_controlled`` is ``True``, it will check if there are two entanglements that fits ``swapping_schema``. If so, it will perfrom swapping spontaneously.
    
    If ``under_controlled`` is ``False``, the swapping will not happen independently.
    In this case, ``NodeSwappingEvent`` should be generate to trigger entanglement swapping.


    :param entity: a ``QuantumNode``
    :param possible: the success rate of swapping
    :param delay: the delay time of swapping operation
    :param fidelity_func: a fidelity function. if it is ``None`` , the default function will be used. In this case, the new generated entanglement's fidelity is f1 \* f2.
    :param bool under_controlled: Whether this node's swapping is under controlled.
    :var swapping_schema: It is the swapping schema in the following format:
        ``[left_hand_nodes,right_hand_nodes]``, where both ``left_hand_nodes`` and ``right_hand_nodes`` is a list of quantum nodes.
    '''
    def __init__(_self, entity, possible=1, delay=0, fidelity_func=None, under_controlled=False):
        _self.entity = entity
        _self.entity.swapping_schema = []
        _self.possible = possible
        _self.delay = delay
        _self.fidelity_func = fidelity_func
        _self.under_controlled = under_controlled

    def install(_self, simulator: Simulator):
        _self.entity.swapping_schema = []
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        '''
        This funcion is called every time when a new entanglement is restored in the `registers`.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters 
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        self = _self.entity
        if _self.under_controlled:
            return

        if self.swapping_schema is None or len(self.swapping_schema) < 2:
            return
        nodes1, nodes2 = self.swapping_schema[0], self.swapping_schema[1]
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
        '''
        The real swapping function. It will aggreate ``e1`` and ``e2`` to distribute a new entanglement.

        :param simulator: the simulator
        :param Entanglement e1: a material entanglement
        :param Entanglement e2: a material entanglement
        '''
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
    '''
    This is the distillation protocol for ``QuantumNode``.

    If ``under_controlled`` is ``True``, it will check if there are two entanglements in ``allow_distillation`` that their fidelity is lower than ``threshold``. If so, it will perfrom distillation spontaneously.
    
    If ``under_controlled`` is ``False``, the swapping will not happen independently.
    In this case, ``NodeDistillationEvent`` should be generate to trigger entanglement swapping.


    :param entity: a ``QuantumNode``
    :param threshold: the lower bound of entanglement's fidelity. It an entanglement's fidelity is lower than ``threshold``, it should be distillated.
    :param delay: the delay time of swapping operation

    :param lazy_run_step: The period that the node should check the fidelity states.
        It is a time in second. If ``lazy_run_step`` is ``None``, periodly check will not happen. In this case, the ``handle`` will be triggled when a new entanglement is restored in the registers.
    :param bool under_controlled: Whether this node's swapping is under controlled.
    :var allow_distillations: a list of nodes. Entanglement between ``entity`` and ``node in allow_distillation`` will be checked.
    '''
    def __init__(_self, entity: QuantumNode, threshold: float = 0, delay: float = 0, lazy_run_step=None, under_controlled=False):
        super().__init__(entity)
        _self.threshold = threshold
        _self.delay = delay
        _self.under_controlled = under_controlled
        _self.lazy_run_step = lazy_run_step

    def install(_self, simulator: Simulator):
        self = _self.entity
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)
        _self.entity.allow_distillation = []
        if _self.lazy_run_step is None:
            return

        lazy_step_time_slice = simulator.to_time_slice(_self.lazy_run_step)
        for i in range(simulator.start_time_slice, simulator.end_time_slice, lazy_step_time_slice):
            self.call(simulator, None, _self, None, i)

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        '''
        This funcion is called every time when a new entanglement is restored in the `registers`.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters 
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
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
        '''
        The real distillation function. It will use ``e1`` and ``e2`` to generate a new entanglement with higher fidelity.

        Default success possibility is ``f_min**2 + (1-f_min)**2`` and defaulty new fidelity is ``f_min**2 / (f_min**2 + (1-f_min)**2)``, where ``f_min = min(e1.fidelity, e2.fidelity)``

        :param simulator: the simulator
        :param Entanglement e1: a material entanglement
        :param Entanglement e2: a material entanglement
        '''
        for n in e1.nodes:
            if n not in e2.nodes:
                log.debug("{} and {} can not used for distillation", e1, e2)
                return

        f_min = min(e1.fidelity, e2.fidelity)
        f = f_min**2 / (f_min**2 + (1-f_min)**2)
        poss = f_min**2 + (1-f_min)**2

        for n in e1.nodes:
            if e1 not in n.registers or e2 not in n.registers:
                log.debug("{} or {} is not in {}", e1, e2, n)
                return

        for n in e1.nodes:
            n.remove_entanglement(e1)
            n.remove_entanglement(e2)

        if random.random() > poss:
            log.debug("{} and {} distillation failure: {}", e1, e2, poss)
            return

        ne = Entanglement(e1.nodes, simulator.current_time, fidelity=f)
        for n in ne.nodes:
            if n.is_full():
                log.debug(
                    "{} and {} distillation failure due to {} is full", e1, e2, n)
                return
        for n in ne.nodes:
            n.add_entanglement(ne)
            ndae = NodeDistillationAfterEvent(simulator.current_time)
            n.call(simulator, ne, self, ndae)
        log.debug("{} distillation successfully", ne)


class KeepUseSoonProtocol():
    '''
    This protocol should be loaded on ``QuantumNode``. It is used to simulate upper-level applications using entanglement.
    It keeps checking whether there is any distributed target entanglement and its fidelity is larger than ``fidelity``.
    If so, it will move that entnaglement into `used_e` and increase the counter `used`.

    :param entity: a ``QuantumNode``
    :param dest: the target destination. The target entanglement should be shared between ``self`` and ``dest``
    :param fidelity: the low bound of fidelity. The entanglement's fidelity must be larger than ``fidelity``
    :var used: the counter of used entanglements.
    :var used_e: the storaged for used entanglements.
    '''
    def __init__(_self, entity, dest, fidelity=0):
        _self.entity = entity
        _self.fidelity = fidelity
        _self.dest = dest
        _self.used = 0
        _self.used_e = []

    def install(_self, simulator: Simulator):
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        '''
        This funcion is called every time when a new entanglement is restored in the `registers`.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters 
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        
        self = _self.entity

        el = [e for e in self.registers if _self.dest in e.nodes and e in _self.dest.registers and e.fidelity >= _self.fidelity]

        for e in el:
            self.remove_entanglement(e)
            _self.dest.remove_entanglement(e)
            # log.debug(f"node {self} used {e}, total used {_self.used}")
            log.exp("{}", _self.used)
            _self.used += 1
            _self.used_e.append(e)

    def total_used_count(_self):
        '''
        This function returns the number in couter ``used``
        :returns int: the number of used entanglements
        '''
        return _self.used

    def total_used_entanglements(_self):
        '''
        This function returns the used entanglements
        :returns: the used entanglements
        '''
        return _self.used_e
