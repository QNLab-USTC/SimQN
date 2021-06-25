import random
from typing import Any, Optional
from qns.schedular import Simulator, Entity, Event
from qns.log import log
from qns.quantum.qubit import *
from .node import Node


class QuantumChannel(Entity):
    '''
        QuantumChannel is an entity of the quantum network.
        It is responsible for simulating the qubit transmission in quantum network.

        :param name: its name.
        :param delay: the delay of transmitting qubit.
        :param loss_rate: the failure probability of transmitting qubit.
        :param bandwidth: the bandwidth of transmitting qubit.
        :param fidelity_model: the fidelity_model coefficient of the quantum channel
        :param nodes: the two nodes connected to the quantum channel.
    '''

    def __init__(self, name: Optional[str] = None, delay: float = 0, loss_rate: float = 0, bandwidth: Optional[int] = None, fidelity_model: Any = None,  precision: float = 1):
        super().__init__(name)
        self.name = name
        self.delay = delay
        self.loss_rate = loss_rate
        self.bandwidth = bandwidth
        self.fidelity_model = fidelity_model
        self.precision = precision
        self.nodes = [None, None]

    def install(self, simulator: Simulator):
        self.simulator = simulator
        self.rate_last_check_time = simulator.start_time_slice
        self.rate_check_period = simulator.to_time_slice(self.precision)
        self.rate_usaged = 0

    def add_nodes(self, node1, node2):
        '''
            This function will connect node1 and node2 through classical channel.

            :param node1: the first node connected to the classical channel.
            :param node2: the second node connected to the classical channel.
        '''
        self.nodes = [node1, node2]

    def handle(self, simulator: Simulator, msg: object, source=None, event=None):
        '''
        ``handle`` is triggered by an ``Event``, It traverses all the protocol to handle this ``event``.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters
        :param source: the entity that send the qubit
        :param event: the event
        '''

        if not isinstance(event, QuantumChannelSendEvent):
            pass

        qubit = event.qubit
        if source is None:
            source = event.source

        if len(self.nodes) != 2:
            raise AssertionError("quantum channel should connect to two nodes")

        if source == self.nodes[0]:
            self.transfer(simulator, qubit, source, self.nodes[1])
        elif source == self.nodes[1]:
            self.transfer(simulator, qubit, source, self.nodes[0])
        else:
            raise AssertionError("error source")

    def default_fidelity_model(self, qubit: Qubit):
        '''
        This function simulate the fidelity change of qubit and it can be rewritten as needed.

        :param qubit: the qubit
        '''
        pass

    def transfer(self, simulator: Simulator, qubit: Qubit, source: Node, destination: Node):
        '''
        This function transfers a message from one node to another node through classical channel.

        :param simulator: the simulator
        :param qubit: the qubit to be transferred
        :param source: the source node
        :param destination: the destination node
        '''

        if random.random() < self.loss_rate:
            log.debug("quantum channel {} : send {} failed", self.name, qubit)
            return

        if self.bandwidth is not None:
            if simulator.current_time_slice >= self.rate_last_check_time + self.rate_check_period:
                self.rate_usaged = 1
                self.rate_last_check_time = simulator.current_time_slice
            else:
                if self.rate_usaged + 1 > self.bandwidth:
                    log.debug("quantum channel {}: drop {}", self.name, qubit)
                    return
                self.rate_usaged += 1

        if self.fidelity_model is not None:
            self.fidelity_model(qubit)
        else:
            self.default_fidelity_model(qubit)

        log.debug(f"quantum link {self.name} send {qubit} to {destination}")

        qre = QuantumChannelReceiveEvent(
            qubit, source, destination, self.simulator.current_time)

        destination.call(simulator, msg=None, source=source, event=qre,
                         time_slice=simulator.current_time_slice + simulator.to_time_slice(self.delay))


class QuantumChannelReceiveEvent(Event):
    def __init__(self, qubit: Qubit, source, destination, init_time: float = None):
        super().__init__(init_time)
        self.qubit = qubit
        self.source = source
        self.destination = destination


class QuantumChannelSendEvent(Event):
    def __init__(self, qubit: Qubit, source, init_time=None):
        super().__init__(init_time)
        self.qubit = qubit
        self.source = source
