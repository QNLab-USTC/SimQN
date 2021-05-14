import random
from qns.schedular import Entity, Simulator, Event
from .basic import Node, Channel

class ClassicSendEvent(Event):
    def __init__(self, init_time, node, msg):
        self.init_time = init_time
        self.node = node
        self.msg = msg
    
    def run(self, simulator:Simulator):
        self.node.inbox.append(self.msg)

class ClassicP2PChannel(Channel):
    def __init__(self, node1, node2, delay: float = 0, drop_rate = 0):
        self.delay = delay
        self.drop_rate = drop_rate
        self.node1 = node1
        self.node2 = node2

        self.inbox1 = []
        self.inbox2 = []
        
    def install(self, simulator: Simulator):
        super().install(simulator)
        self.node1.link = self.inbox1
        self.node2.link = self.inbox2
        self.delay_time_slice = simulator.to_time_slice(self.delay)

    def handle(self, simulator: Simulator):
        for msg in self.inbox1:
            if random.random() < self.drop_rate:
                pass
            se = ClassicSendEvent(simulator.to_time(simulator.current_time_slice), self.node2, msg)
            simulator.add_event(simulator.current_time_slice + self.delay_time_slice, se)
            self.inbox1.clear()
        for msg in self.inbox2:
            if random.random() < self.drop_rate:
                pass
            se = ClassicSendEvent(simulator.to_time(simulator.current_time_slice), self.node1, msg)
            simulator.add_event(simulator.current_time_slice + self.delay_time_slice, se)
            self.inbox2.clear()


class ClassicSender(Node):
    def __init__(self, start_time: float, end_time: float, step_time: float, message: str):
        super().__init__()
        self.start_time = start_time
        self.end_time = end_time
        self.step_time = step_time
        self.message = message
        self.link = None

        self.start_time_slice = None

    def handle(self, simulator: Simulator):
        super().handle(simulator)
        if self.link is None:
            raise Exception("no class link attached")

        if self.start_time_slice is None:
            self.start_time_slice = simulator.to_time_slice(self.start_time)
            if self.end_time is not None:
                self.end_time_slice = simulator.to_time_slice(self.end_time)
            if self.step_time is not None:
                self.step_time_slice = simulator.to_time_slice(self.step_time)

        if self.end_time is None or self.step_time is None:
            if simulator.current_time_slice == self.start_time_slice:
                print("Sender: time", simulator.current_time, "send", self.message)
                self.link.append(self.message)
        else:
            if simulator.current_time_slice >= self.start_time_slice and \
                simulator.current_time_slice <= self.end_time_slice and \
                (simulator.current_time_slice - self.start_time_slice) % self.step_time_slice == 0:
                print("Sender: time", simulator.current_time, "send", self.message)
                self.link.append(self.message)

class ClassicReceiver(Node):
    def __init__(self):
        super().__init__()
        self.link = None
    
    def handle(self, simulator: Simulator):
        for msg in self.inbox:
            print("receiver: time ", simulator.current_time, "recv", msg)
        self.inbox.clear()

class ClassicRepeaterEvent(Event):
    def __init__(self, init_time, outbox, msg):
        self.init_time = init_time
        self.outbox = outbox
        self.msg = msg
    
    def run(self, simulator:Simulator):
        print("repeater: ", simulator.current_time, "send", self.msg)
        self.outbox.append(self.msg)

class ClassicRepeater(Node):
    def __init__(self, delay: float = 0):
        super().__init__()
        self.link = None
        self.buffer = []
        self.delay = delay
        self.delay_time_slice = -1
    
    def handle(self, simulator: Simulator):
        if self.delay_time_slice == -1:
            self.delay_time_slice = simulator.to_time_slice(self.delay)

        for msg in self.inbox:
            print("repeater: time ", simulator.current_time, "recv", msg)
            cre = ClassicRepeaterEvent(simulator.current_time, self.link, msg)
            simulator.add_event(simulator.current_time_slice + self.delay_time_slice, cre)
        self.inbox.clear()
