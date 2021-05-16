from .simulator import Simulator


class Protocol():
    def __init__(_self, entity):
        _self.entity = entity

    def install(_self, simulator: Simulator):
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        pass
