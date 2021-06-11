import random
from qns.topo import Channel
from qns.schedular import Simulator, Entity, Event
from qns.log import log


class ClassicChannel(Entity):
    '''
        ClassicalChannel is an entity of the quantum network.
        It is responsible for simulating the message transmission in classical network.

        :param name: its name.
        :param delay: the delay of transmitting message.
        :param loss_rate: the failure probability of transmitting message.
        :param bandwith: the bandwith of transmitting message.
        :param nodes: the two nodes connected to the classical channel.
    '''

    def __init__(self, name, delay, loss_rate, bandwith):
        super().__init__(name)
        self.name = name
        self.delay = delay
        self.loss_rate = loss_rate
        self.bandwith = bandwith
        self.nodes = [0, 0]

    def add_nodes(self, node1, node2):
        '''
            This function will connect node1 and node2 through classical channel.

            :param node1: the first node connected to the classical channel.
            :param node2: the second node connected to the classical channel.
        '''
        self.nodes[0] = (node1)
        self.nodes[1] = (node2)

    def handle(self, simulator: Simulator, msg: object, source=None, event=None):
        '''
        ``handle`` is triggered by an ``Event``, It traverses all the protocol to handle this ``event``.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters
        :param source: the entity that generated the ``event``
        :param event: the event
        '''
        self.event = event
        if self.event == ClassicTransferEvent:
            if source == self.nodes[0]:
                self.transfer(simulator, msg, self.nodes[0], self.nodes[1])
            else:
                self.transfer(simulator, msg, self.nodes[1], self.nodes[0])

    def transfer(self, simulator: Simulator, message: object, source=None, destination=None):
        '''
        This function transfers a message from one node to another node through classical channel.

        :param simulator: the simulator
        :param message: the message to be transferred
        :param source: the source node
        :param destination: the destination node
        '''

        if random.random() < self.loss_rate:
            log.debug("fiber: send {} failed", message)
            simulator.add_event(
                simulator.current_time_slice, ClassicTransferFEvent(simulator.current_time_slice))
            return

        if self.delay is not None:
            log.debug(f"link {self} send {message} to {destination.name}")
            cre = ClassicReceiveEvent(
                destination_node=destination, msg=message, source_node=source)

            simulator.add_event(
                simulator.current_time_slice + simulator.to_time_slice(self.delay), cre)


class ClassicReceiveEvent(Event):

    def __init__(self, destination_node, msg, source_node=None, init_time: float = None):
        super().__init__(init_time)
        self.msg = msg
        self.source_node = source_node
        self.destination_node = destination_node

    def run(self, simulator: Simulator):
        simulator.add_event(
            simulator.current_time_slice, ClassicTransferSEvent(simulator.current_time_slice))
        self.destination_node.call(simulator=simulator, msg=self.msg,
                                   source=self.source_node, event=self)


class ClassicTransferEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)


class ClassicTransferSEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        print(f"time:{simulator.current_time} transfer message successfully!")


class ClassicTransferFEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        print(f"time:{simulator.current_time} transfer message failed!")
