from qns.entangled.node import QuantumNodeDistillationProtocol
from qns.entangled import NodeDistillationEvent, QuantumNodeSwappingProtocol, NodeSwappingEvent, Entanglement
from qns.schedular import Protocol, Simulator, Event
from qns.topo import Node
from qns.log import log
import uuid


class QuantumController(Node):
    '''
    This is a controller in quantum network. It could be an SDN controller.
    It is used to arrange swapping and distillation.

    :param nodes: the list of ``QuantumNode`` that it controlled.
    :param links: the list of ``QuantumChannel`` that it controlled.
    :param name: its name
    '''
    def __init__(self, nodes=[], links=[], name=None):
        self.nodes = nodes
        self.links = links
        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

    def __repr__(self) -> str:
        return "<controller {}>".format(self.name)


class ControllerEvent(Event):
    '''
    This event will call ``ControllerProtocol``'s ``run`` function for
    centralized decision.

    :param protocol: the ``ControllerProtocol``
    :param init_time: the event's generation time in second
    '''
    def __init__(self, protocol, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol

    def run(self, simulator: Simulator):
        # self.node.call(simulator, (self.e1, self.e2),
        #  self.source, event=self)
        self.protocol.run(simulator)


class ControllerProtocol(Protocol):
    '''
    This protocol is used as a simple controller application.
    It will first perfrom distillation on those entanglements that satisfies ``distillation_schema``.
    Then, it will perfrom swapping on those who satisfies ``swapping_schema``.

    :param entity: the ``QuantumController``
    :param period: the period time that the controller makes a decision
    :param delay: the delay time it used to make a decision
    :param distillation_schema: the distillation schema is a list of ``(u,v)``,
         where entanglements between (u,v) will check distillation
    :param distillation_threshold: if an entanglement's fidelity is lower than ``distillation_threshold``, 
        it will be used in distillation
    :param swapping_schema: the swapping schema is a set of ``{swapping_node: (start_nodes, end_nodes)}``, 
        where ``start_nodes`` and ``end_nodes`` is a list of quantum nodes.
    :param swapping_possible: the success possibility of swapping.

    An example of ``distillation_schema`` is:

    .. code-block:: python

        distillation_schema = [(n1, n2), (n1, n3), (n1, n4), 
            (n2, n3), (n2, n4), (n3, n4)]

    An example of ``swapping_schema`` is:

    .. code-block:: python

        swapping_schema = { 
            n2: ([n1], [n3]), 
            n3: ([n1], [n4])
        }
    '''
    def __init__(_self, entity: QuantumController, period=0.5, delay=0, distillation_schema=[], distillation_threshold=0.8, swapping_schema={}, swapping_possible=1):
        super().__init__(entity)
        _self.period = period
        _self.delay = delay
        _self.distillation_schema = distillation_schema
        _self.swapping_schema = swapping_schema
        _self.distillation_threshold = distillation_threshold
        _self.swapping_possible = swapping_possible

    def install(_self, simulator: Simulator):
        '''
        Insert ``ControllerEvent`` into ``simulator``. Those events will be called periodly.

        :param simulator: the simulator
        '''
        _self.period_time_slice = simulator.to_time_slice(_self.period)
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

        for i in range(simulator.start_time_slice, simulator.end_time_slice, _self.period_time_slice):
            controllerevent = ControllerEvent(_self, simulator.current_time)
            simulator.add_event(i, controllerevent)

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity  # self is a QuantumNode
        pass

    def run(_self, simulator):
        '''
        The real decision function. Those entangled qubits will be check for distillation frist and than swapping.
        Then, ``NodeDistillationEvent`` and ``NodeSwappingEvent`` will be generate to process swapping or distillation.

        :param simulator: the simulator
        '''
        self = _self.entity

        # retrive all entangled qubit
        entanglement_set = []
        for node in self.nodes:
            for e in node.registers:
                if e not in entanglement_set:
                    entanglement_set.append(e)

        # handle distillation
        need_distillation = [e for e in entanglement_set for (
            n1, n2) in _self.distillation_schema if n1 in e.nodes and n2 in e.nodes and e.fidelity <= _self.distillation_threshold]

        map = []
        used = []
        for e in need_distillation:
            for en in need_distillation:
                if en == e:
                    continue
                if len(e.nodes) == len(en.nodes) == len(set(e.nodes) & set(en.nodes)):
                    map.append((e, en))
                    used.append(e)
                    used.append(en)

        for (e1, e2) in map:
            log.debug(
                "controller: distillation start on {} using {} and {}", self, e1, e2)
            fackprotocol = QuantumNodeDistillationProtocol(
                e1, _self.distillation_threshold, _self.delay)
            ede = NodeDistillationEvent(fackprotocol, e1, e2)
            simulator.add_event(
                simulator.current_time_slice + _self.delay_time_slice, ede)

        # handled swapping
        unused = list(set(entanglement_set) - set(used))
        for swap_node, (nodes1, nodes2) in _self.swapping_schema.items():
            e_set1, e_set2 = [], []
            for e in swap_node.registers:
                for n in e.nodes:
                    if n == swap_node:
                        continue
                    if n in nodes1:
                        e_set1.append(e)
                    if n in nodes2:
                        e_set2.append(e)

            map = zip(e_set1, e_set2)
            for e1, e2 in map:
                log.debug("controller: swap start using {} and {}", e1, e2)
                fackprotocol = QuantumNodeSwappingProtocol(
                    swap_node, _self.swapping_possible, _self.delay)
                swapevent = NodeSwappingEvent(fackprotocol, e1, e2)
                simulator.add_event(simulator.current_time_slice +
                                    _self.delay_time_slice, swapevent)
