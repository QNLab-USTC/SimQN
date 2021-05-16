from .simulator import Simulator
from .event import Event
from .entity import Entity

class Protocol():
    def __init__(self, entity: Entity):
        self.entity = entity

    def install(self, simulator: Simulator):
        pass

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        pass