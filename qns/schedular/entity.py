from .event import Event
from .simulator import Simulator

# The super object of every entities in qns including nodes, channels and others.
# Must implement `handle` function
class Entity():
    def __init__(self):
        self.inbox = []
        self.outbox = []

    def install(_self, simulator: Simulator):
        class EntityHandleEvent(Event):
            def run(self, simulator):
                _self.handle(simulator)
        
        handleEvent = EntityHandleEvent()
        i = simulator.start_time_slice
        while i <= simulator.end_time_slice:
            simulator.add_event(i, handleEvent)
            i += 1

    def handle(self, simulator):
        raise NotImplemented