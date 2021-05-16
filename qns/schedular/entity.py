from typing import Protocol
from .event import Event
from .simulator import Simulator

# The super object of every entities in qns including nodes, channels and others.
# Must implement `handle` function


class Entity():
    def __init__(self):
        self.protocols = []

    def install(self, simulator: Simulator):
        for p in self.protocols:
            p.install(simulator)

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        for p in self.protocols:
            p.handle(simulator, msg, source, event)

    def inject_protocol(self, protocal):
        if not hasattr(self, "protocols"):
            self.protocols = []
        self.protocols.append(Protocol)
