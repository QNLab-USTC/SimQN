from .event import Event
from .simulator import Simulator

class Entity():
    def __init__(self):
        pass

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