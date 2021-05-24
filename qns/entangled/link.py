
import random
from qns.entangled.entanglement import Entanglement
from qns.topo import Channel
from qns.schedular import Simulator, Event, Protocol
from .events import GenerationAllocateEvent, GenerationEntanglementAfterEvent, GenerationEvent
from qns.log import log


class QuantumChannel(Channel):
    '''
    This is a quantum channel. It is used to modeling a EPR generator.

    :param nodes: a list of nodes that attached on this EPR generator.
    :param str name: its name
    '''
    def __init__(self, nodes=[],  name=None):
        super().__init__(name)
        self.nodes = nodes

    def __repr__(self):
        return "<link " + self.name+">"


class GenerationProtocal(Protocol):
    '''
    This is the entanglement generation protocol for ``QuantumChannel``.
    This protocol will generate new entanglements continuously.

    There will be a great overhead if every ``GenerationEvent`` is produced before the simulator runs.
    Setting an appropriate ``allocate_step`` can effectively reduce the initialization time.

    :param entity: a ``QuantumChannel``.
    :param possible: the success possibility of generate an entanglement.
    :param rate: generate ``rate`` new entanglements per second.
    :param delay: the delay time for each generation.
    :param fidelity: the initial fidelity of generated entanglement.
    :param allocate_step: the step time to schedule the next several ``GenerationEvent``. The default value is ``1`` second.
    :param under_controlled: whether the EPR will generate spontaneously. If ``under_controlled`` is ``False``, it will generate entanglements when ``generation`` is called. 
    '''
    def __init__(_self, entity, possible=1, rate=10, delay=0.02, fidelity=1, allocate_step=1, under_controlled = False):
        super().__init__(entity)
        _self.possible = possible
        _self.delay = delay
        _self.fidelity = fidelity
        _self.rate = rate
        _self.step = allocate_step
        _self.under_controlled = under_controlled

    def install(_self, simulator: Simulator):
        '''
        Install ``GenerationAllocateEvent`` events into ``simulator`` before it runs.

        :param simulator: the simulator
        '''
        self = _self.entity
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

        for n in self.nodes:
            n.links.append(self)

        if _self.under_controlled:
            return

        # ge = GenerationEvent(_self, simulator.current_time)
        gae = GenerationAllocateEvent(_self, simulator.current_time)
        start_time_slice = simulator.start_time_slice
        end_time_slice = simulator.end_time_slice
        # step_time_slice = int(simulator.time_accuracy / _self.rate)
        _self.allocate_step_time_slice = simulator.to_time_slice(_self.step)
        for t in range(start_time_slice, end_time_slice, _self.allocate_step_time_slice):
            simulator.add_event(t, gae)

    def allocate(_self, simulator: Simulator):
        '''
        The functions is called by ``GenerationAllocateEvent``
        It will arrange the ``GenerationEvent`` in the following ``allocate_step`` second.

        :param simulator: the simulator
        '''
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
        '''
        This is the real generation function, it generat new entanglement ``e`` 
        and use ``GenerationEntanglementAfterEvent`` event to notify ``nodes`` to store new entanglemnt.

        :param simulator: the simulator
        '''
        self = _self.entity

        if random.random() > _self.possible:
            log.debug("{} generation failed".format(self))
            return

        e = Entanglement(
            self.nodes, simulator.current_time_slice, fidelity=_self.fidelity)
        geae = GenerationEntanglementAfterEvent(
            e, self, self.nodes, simulator.current_time)
        simulator.add_event(simulator.current_time_slice +
                            _self.delay_time_slice, geae)
