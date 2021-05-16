
from .protocol import Protocol
from .event import Event
from .simulator import Simulator
from qns.schedular import simulator

# The super object of every entities in qns including nodes, channels and others.
# Must implement `handle` function


class Entity():
    def __init__(self):
        self.protocols = []

    def install(self, simulator: Simulator):
        self.simulator = simulator
        for p in self.protocols:
            p.install(simulator)

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        for p in self.protocols:
            p.handle(simulator, msg, source, event)

    def call(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        callevent = CallEvent(self, simulator, msg, source, event)
        simulator.add_event(simulator.current_time_slice, callevent)

    def inject_protocol(self, protocol):
        if not hasattr(self, "protocols"):
            self.protocols = []
        if isinstance(protocol, list):
            for p in protocol:
                self.protocols.append(p)
        else:
            self.protocols.append(protocol)

class CallEvent(Event):
    def __init__(self, callee, simulator: Simulator, msg: object, source=None, event: Event = None):
        self.simulator = simulator
        self.msg = msg
        self.source = source
        self.event = event
        self.callee = callee

    def run(self, simulator):
        self.callee.handle(self.simulator, self.msg, self.source, self.event)