import uuid
from qns.schedular import Simulator, Protocol, Event
from qns.topo import Node
from qns.log import log

class ClassicNode(Node):
    def __init__(self, name=None):
        self.classic_links = []

        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

    def __repr__(self):
        return "<classic node " + self.name+">"


# call msg = (link, data) to send
class ClassicSendProtocol(Protocol):
    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        _self.simulator = simulator

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        self = _self.entity
        (link, data) = msg
        if link not in self.classic_links:
            log.debug("link {} is not attached on {}", link, self)

        log.debug("{} send {} on {}", self, data, link)
        link.call(simulator, data, source=self, event=event)


class ClassicRecvProtocol(Protocol):
    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        _self.simulator = simulator

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        self = _self.entity
        data = msg
        source = source

        log.debug("{} recv {} from {}",
                  self, data, source)
