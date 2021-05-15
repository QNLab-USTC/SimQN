from .event import Event
from .simulator import Simulator

# The super object of every entities in qns including nodes, channels and others.
# Must implement `handle` function
class Entity():
    def __init__(self):
        pass

    def install(self, simulator: Simulator):
        # class EntityHandleEvent(Event):
        #     def run(self, simulator):
        #         _self.handle(simulator)
        
        # handleEvent = EntityHandleEvent()
        # i = simulator.start_time_slice
        # while i <= simulator.end_time_slice:
        #     simulator.add_event(i, handleEvent)
        #     i += 1
        raise NotImplemented

    def handle(self, simulator: Simulator, msg: object, source = None , event: Event = None):
        raise NotImplemented