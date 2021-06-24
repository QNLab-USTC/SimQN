import random
from qns.topo import Channel
from qns.schedular import Simulator, Entity, Event
from qns.log import log
from .node import Node


class ClassicChannel(Entity):
    '''
        ClassicalChannel is an entity of the quantum network.
        It is responsible for simulating the message transmission in classical network.

        :param name: its name.
        :param delay: the delay of transmitting message.
        :param loss_rate: the failure probability of transmitting message.
        :param bandwidth: the bandwidth of transmitting message.
        :param nodes: the two nodes connected to the classical channel.
    '''

    def __init__(self, name, delay: float =0, loss_rate: float =0, bandwidth: int =None, precision: float = 1):
        super().__init__(name)
        self.name = name
        self.delay = delay
        self.loss_rate = loss_rate
    
        self.bandwidth = bandwidth
        self.precision = precision

        self.nodes = [None, None]

    def install(self, simulator: Simulator):
        self.simulator = simulator
        self.rate_last_check_time = simulator.start_time_slice
        self.rate_check_period = simulator.to_time_slice(self.precision)
        self.rate_usaged = 0

    def add_nodes(self, node1: Node, node2: Node):
        '''
            This function will connect node1 and node2 through classical channel.

            :param node1: the first node connected to the classical channel.
            :param node2: the second node connected to the classical channel.
        '''
        self.nodes = [node1, node2]

    def handle(self, simulator: Simulator, msg: object, source: Node = None, event = None):

        if len(self.nodes) != 2:
            raise AssertionError("line must be connected to two nodes")

        if isinstance(event, ClassicTransferEvent):
            if source == self.nodes[0]:
                self.transfer(simulator, msg, self.nodes[0], self.nodes[1])
            else:
                self.transfer(simulator, msg, self.nodes[1], self.nodes[0])

    def transfer(self, simulator: Simulator, message: object, source: Node, destination: Node):
        '''
        This function transfers a message from one node to another node through classical channel.

        :param simulator: the simulator
        :param message: the message to be transferred
        :param source: the source node
        :param destination: the destination node
        '''

        if random.random() < self.loss_rate:
            log.debug("fiber: send {} failed", message)
            # simulator.add_event(
            #     simulator.current_time_slice, ClassicTransferFEvent(simulator.current_time_slice))
            return
        
        if self.bandwidth is not None:
            if simulator.current_time_slice >= self.rate_last_check_time + self.rate_check_period:
                self.rate_usaged = len(message)
                self.rate_last_check_time = simulator.current_time_slice
            else:
                if self.rate_usaged + len(message) > self.bandwidth:
                    log.debug("fiber {}: drop {}", self.name ,message)
                    return
                self.rate_usaged += len(message)

        log.debug(f"link {self} send {message} to {destination.name}")

        cre = ClassicReceiveEvent(
            destination_node=destination, msg=message, source_node=source)
        
        destination.call(simulator, message, source, cre, simulator.current_time_slice + simulator.to_time_slice(self.delay))



class ClassicReceiveEvent(Event):
    def __init__(self, destination_node: Node, msg, source_node: Node =None, init_time: float = None):
        super().__init__(init_time)
        self.msg = msg
        self.source_node = source_node
        self.destination_node = destination_node

    def run(self, simulator: Simulator):
        # self.destination_node.call(simulator=simulator, msg=self.msg,
        #              source=self.source, event=self)
        pass


class ClassicTransferEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

