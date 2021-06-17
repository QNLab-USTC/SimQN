from qns.schedular import Simulator, Protocol, Event
from inspect import isgeneratorfunction

class NodeProtocol(Protocol):
    def install(_self, simulator: Simulator):
        if isgeneratorfunction(_self.run):
            _self.is_generator = True
        else:
            _self.is_generator = False

    def handle(_self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self = _self.entity
        if _self.is_generator:
            _self.run()
        else:
            pass

    def run(self, simulator: Simulator, ):
        pass