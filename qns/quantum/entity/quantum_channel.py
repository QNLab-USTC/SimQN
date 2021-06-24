import random
from qns.schedular import Simulator, Entity, Event
from qns.log import log
from qns.quantum.qubit import *


class QuantumChannel(Entity):
    '''
        QuantumChannel is an entity of the quantum network.
        It is responsible for simulating the qubit transmission in quantum network.

        :param name: its name.
        :param delay: the delay of transmitting qubit.
        :param loss_rate: the failure probability of transmitting qubit.
        :param bandwith: the bandwith of transmitting qubit.
        :param decoherence: the decoherence coefficient of the quantum channel
        :param nodes: the two nodes connected to the quantum channel.
    '''

    def __init__(self, name, delay, loss_rate, bandwith, decoherence=None):
        super().__init__(name)
        self.name = name
        self.delay = delay
        self.loss_rate = loss_rate
        self.bandwith = bandwith
        self.decoherence = decoherence
        self.nodes = [0, 0]

    def add_nodes(self, node1, node2):
        '''
            This function will connect node1 and node2 through classical channel.

            :param node1: the first node connected to the classical channel.
            :param node2: the second node connected to the classical channel.
        '''
        self.nodes[0] = node1
        self.nodes[1] = node2

    def handle(self, simulator: Simulator, qubit: object, source=None, event=None):
        '''
        ``handle`` is triggered by an ``Event``, It traverses all the protocol to handle this ``event``.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters
        :param source: the entity that generated the ``event``
        :param event: the event
        '''
        self.event = event
        if self.event == QuantumTransferEvent:
            self.transfer(simulator, qubit)

    def deco_function(self, decoherence, qubit):
        '''
        This function simulate the variation of qubit and it can be rewritten as needed.

        :param decoherence: the decoherence coefficient of the quantum channel
        :param qubit: the qubit
        '''
        pass

    def transfer(self, simulator: Simulator, qubit: object, source=None, destination=None):
        '''
        This function transfers a message from one node to another node through classical channel.

        :param simulator: the simulator
        :param qubit: the qubit to be transferred
        :param source: the source node
        :param destination: the destination node
        '''

        if random.random() < self.loss_rate:
            log.debug("fiber: send {} failed", qubit)
            simulator.add_event(
                simulator.current_time_slice, QuantumTransferFEvent(simulator.current_time_slice))
            return
        if self.decoherence is not None:
            self.decoFunction(self.decoherence, qubit)

        if self.delay is not None:
            log.debug(f"link {self} send {qubit} to {destination.name}")
            qre = QuantumReceiveEvent(
                destination_node=destination, qubit=qubit, source_node=source)

            simulator.add_event(
                simulator.current_time_slice + simulator.to_time_slice(self.delay), qre)


class QuantumReceiveEvent(Event):

    def __init__(self, destination_node, qubit, source_node, init_time: float = None):
        super().__init__(init_time)
        self.qubit = qubit
        self.source_node = source_node
        self.destination_node = destination_node

    def run(self, simulator: Simulator):
        simulator.add_event(
            simulator.current_time_slice, QuantumTransferSEvent(simulator.current_time_slice))
        self.destination_node.call(simulator=simulator, msg=self.qubit,
                                   source=self.source_node, event=self)


class QuantumTransferEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)


class QuantumTransferSEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        print(f"time:{simulator.current_time} transfer qubit successfully!")


class QuantumTransferFEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        print(f"time:{simulator.current_time} transfer qubit failed!")
