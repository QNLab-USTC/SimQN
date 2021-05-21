import uuid
from qns.schedular import Simulator, Protocol, Event
from qns.topo import Node
from qns.log import log
from .message import Message

class ClassicNode(Node):
    def __init__(self, name=None):
        self.classic_links = []

        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

    def __repr__(self):
        return "<classic node " + self.name+">"


class ClassicSendProtocol(Protocol):
    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        _self.simulator = simulator

    def handle(_self, simulator: Simulator, msg: Message, source=None, event=None):
        self = _self.entity
        link = msg.link

        if link not in self.classic_links:
            log.debug("link {} is not attached on {}", link, self)

        log.debug("{} send {} on {}", self, msg, link)
        link.call(simulator, msg, source=self, event=event)


class ClassicRecvProtocol(Protocol):
    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        _self.simulator = simulator

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        self = _self.entity

        log.debug("{} recv {} from {}",
                  self, msg, source)

# ClassicSwitchProtocol
# forwarding table = {outnode1: outlink1, outnode2: outlink2}
# buffer_size maximun buffer size
# delay delay time in seconde
class ClassicSwitchProtocol(Protocol):
    def __init__(_self, entity,forwarding = {}, delay = 0 ,buffer_size = None):
        super().__init__(entity)
        _self.delay = delay
        _self.forwarding = forwarding
        _self.buffer_size = buffer_size

    def install(_self, simulator: Simulator):
        _self.simulator = simulator
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

    def handle(_self, simulator: Simulator, msg: Message, source=None, event=None):
        self = _self.entity
        try: 
            link = _self.forwarding[msg.to_node]
        except KeyError:
            log.debug("{} can not forward to node {} ", self, source)
            return
        log.debug("{} send {} on {}", self, msg, link)
        link.call(simulator, msg, source=self, event=event, time_slice = simulator.current_time_slice + _self.delay_time_slice)  