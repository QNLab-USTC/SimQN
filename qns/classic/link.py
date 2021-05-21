import uuid
import random
from qns.topo import Channel
from qns.schedular import Protocol, Simulator
from qns.log import log
from .event import ClassicReceiveEvent

class ClassicLink(Channel):
    def __init__(self, nodes=[], name=None):
        self.classic_nodes = nodes

        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

    def __repr__(self):
        return "<classic link " + self.name+">"


# ClassicLinkProtocol
# entity: ClassicLink
# delay: dalay time in second
# possible: 1-drop possibility
# rate: byte per second
# precision: check rate precision in second
class ClassicLinkProtocol(Protocol):
    def __init__(_self, entity ,delay=0, possible=1, rate=None,	precision = 1):
        super().__init__(entity)
        _self.delay = delay
        _self.possible = possible
        _self.rate = rate
        _self.precision = precision

    def install(_self, simulator: Simulator):
        _self.simulator = simulator
        self = _self.entity
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

        _self.rate_last_check_time = simulator.start_time_slice
        _self.rate_check_period = simulator.to_time_slice(_self.precision)
        _self.rate_usaged = 0

        for n in self.classic_nodes:
            n.classic_links.append(self)

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        self = _self.entity

        if len(self.classic_nodes) != 2:
            log.debug("fiber: break link")
            return
        
        if random.random() > _self.possible:
            log.debug("fiber: send {} failed", msg)
            return

        # throughput check
        if _self.rate is not None:
            if simulator.current_time_slice >= _self.rate_last_check_time + _self.rate_check_period:
                _self.rate_usaged = len(msg)
                _self.rate_last_check_time = simulator.current_time_slice
            else:
                if _self.rate_usaged + len(msg) > _self.rate:
                    log.debug("fiber: drop {}", msg)
                    return
                _self.rate_usaged += len(msg)
            

        for n in self.classic_nodes:
            if n == source:  # do not send back
                continue
            else:
                log.debug(f"link {self} send {msg} to {n}")
                cre = ClassicReceiveEvent(
                    to=n, msg = msg, source=source)

                simulator.add_event(
                    simulator.current_time_slice + _self.delay_time_slice, cre)