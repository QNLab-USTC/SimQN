from qns.schedular.entity import Entity
import random
from qns.schedular import Simulator, Event, simulator
from .basic import Node, Channel


class ClassicP2PChannel(Channel):
    def __init__(self, node1, node2, delay: float = 0, drop_rate=0):
        self.delay = delay
        self.drop_rate = drop_rate
        self.node1 = node1
        self.node2 = node2

    def install(self, simulator: Simulator):
        self.delay_time_slice = simulator.to_time_slice(self.delay)
        self.node1.links.append(self)
        self.node2.links.append(self)

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):

        class RecvEvent(Event):
            def __init__(self, from_node, to_node, link, msg):
                self.link = link
                self.from_node = from_node
                self.to_node = to_node
                self.msg = msg

            def run(self, simulator):
                self.to_node.handle(simulator, self.msg, self.link, self)

        if source == self.node1:
            # handle drop
            if random.random() < self.drop_rate:
                print("link drop")
                return
            # handle delay
            re = RecvEvent(self.node1, self.node2, self, msg)
            simulator.add_event(
                simulator.current_time_slice + self.delay_time_slice, re)

        if source == self.node2:
            # handle drop
            if random.random() < self.drop_rate:
                print("link drop")
                return
            # handle delay
            re = RecvEvent(self.node2, self.node1, self, msg)
            simulator.add_event(
                simulator.current_time_slice + self.delay_time_slice, re)


class ClassicSender(Node):
    def __init__(self, start_time: float, end_time: float, step_time: float, message: str):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.step_time = step_time
        self.message = message
        self.links = []

        self.start_time_slice = None

    def install(self, simulator: Simulator):
        self.start_time_slice = simulator.to_time_slice(self.start_time)
        self.end_time_slice = simulator.to_time_slice(self.end_time)
        self.step_time_slice = simulator.to_time_slice(self.step_time)

        class SendEvent(Event):
            def __init__(self, node, link: Entity, msg):
                self.link = link
                self.node = node
                self.msg = msg

            def run(self, simulator: Simulator):
                print("Send: [", simulator.current_time, "]", self.msg)
                self.link.handle(simulator, self.msg, self.node, self)

        for i in range(self.start_time_slice, self.end_time_slice, self.step_time_slice):
            for link in self.links:
                se = SendEvent(self, link, self.message+str(i))
                simulator.add_event(i, se)


class ClassicReceiver(Node):
    def __init__(self):
        self.links = []

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        print("Recv: [", simulator.current_time, "]", msg)


class ClassicRepeaterEvent(Event):
    def __init__(self, init_time, outbox, msg):
        self.init_time = init_time
        self.outbox = outbox
        self.msg = msg

    def run(self, simulator: Simulator):
        print("repeater: ", simulator.current_time, "send", self.msg)
        self.outbox.append(self.msg)


class ClassicRepeater(Node):
    def __init__(self, delay: float = 0):
        super().__init__()
        self.links = []
        self.buffer = []
        self.delay = delay
        self.delay_time_slice = -1

    def install(self, simulator: Simulator):
        self.delay_time_slice = simulator.to_time_slice(self.delay)

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        print("RepR: [", simulator.current_time, "]", msg)

        class SendEvent(Event):
            def __init__(self, node, link: Entity, msg):
                self.link = link
                self.node = node
                self.msg = msg

            def run(self, simulator: Simulator):
                print("RepS: [", simulator.current_time, "]", self.msg)
                self.link.handle(simulator, self.msg, self.node, self)

        for link in self.links:
            if link == source:
                continue
            se = SendEvent(self, link, msg)
            simulator.add_event(
                simulator.current_time_slice + self.delay_time_slice, se)
