from qns.schedular import Simulator, Protocol, Event
from inspect import isgeneratorfunction

class NodeProtocol(Protocol):

    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        if isgeneratorfunction(_self.run):
            _self.gr = _self.run(simulator)
            _self.gr.send(None)
        else:
            _self.gr = None

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity
        if _self.gr is not None:
            _self.gr.send((msg, source, event))
        else:
            _self.run(simulator, msg, source, event)

    def run(_self, simulator: Simulator, msg: object = None, source=None, event: Event = None):
        # (msg, source, event) = yield None
        # or
        raise NotImplemented