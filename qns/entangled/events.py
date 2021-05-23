from qns.schedular.entity import Entity
from typing import SupportsRound
from qns.schedular import Event, Simulator
from .entanglement import Entanglement
from qns.log import log


class GenerationAllocateEvent(Event):
    '''
    This event will call ``GenerationProtocal``'s ``allocate`` function to 
    arrange ``GenerationEvent`` in the following step time.

    :param protocol: the ``GenerationProtocal``
    :param init_time: the event's generation time in second
    '''
    def __init__(self, protocol, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol

    def run(self, simulator: Simulator):
        self.protocol.allocate(simulator)


class GenerationEvent(Event):
    '''
    This event will call ``GenerationProtocal``'s ``generation`` function to 
    generate new entanglement

    :param protocol: the ``GenerationProtocal``
    :param init_time: the event's generation time in second
    '''
    def __init__(self, protocol, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol

    def run(self, simulator: Simulator):
        self.protocol.generation(simulator)


class GenerationEntanglementAfterEvent(Event):
    '''
    This event is called after an entangment is generated. 
    It will store entanglement into ``nodes``'s registers.

    :param e: the generated entanglement
    :param link: the ``QuantumChannel`` EPR Generator
    :param nodes: ``e`` is shared between ``nodes``
    :param init_time: the event's generation time in second
    '''
    def __init__(self, e: Entanglement, link, nodes, init_time: float = None):
        super().__init__(init_time)
        self.link = link
        self.nodes = nodes
        self.e = e

    def run(self, simulator: Simulator):
        '''
        This function will add ``e`` in ``nodes``'s registers and notify them the new coming entanglement.

        :param simulator: the simulator
        '''
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
    '''
    This event will call ``QuantumNodeSwappingProtocol``'s ``swapping`` function for
    entanglement swapping.

    :param protocol: the ``QuantumNodeSwappingProtocol``
    :param e1: the material entanglement
    :param e2: the material entanglement
    :param source: the ``QuantumNode`` that perfrom swapping
    :param init_time: the event's generation time in second
    '''
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
    '''
    This event is used to notify ``node`` about the swapping.

    :param node: the ``QuantumNode`` that should receive the new entanglement
    :param init_time: the event's generation time in second
    '''
    def __init__(self, node, init_time: float = None):
        super().__init__(init_time)
        self.node = node

    def run(self, simulator: Simulator):
        pass


class NodeDistillationEvent(Event):
    '''
    This event will call ``QuantumNodeDistillationProtocol``'s ``distillation`` function for
    entanglement distillation.

    :param protocol: the ``QuantumNodeDistillationProtocol``
    :param e1: the material entanglement
    :param e2: the material entanglement
    :param init_time: the event's generation time in second
    '''
    def __init__(self, protocol, e1: Entanglement, e2: Entanglement, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol
        self.e1 = e1
        self.e2 = e2

    def run(self, simulator: Simulator):
        self.protocol.distillation(simulator, self.e1, self.e2)


class NodeDistillationAfterEvent(Event):
    '''
    This event is used to notify ``node`` about the distillation.

    :param node: the ``QuantumNode`` that should receive the new entanglement
    :param init_time: the event's generation time in second
    '''
    def __init__(self, node, init_time: float = None):
        super().__init__(init_time)
        self.node = node

    def run(self, simulator: Simulator):
        pass
