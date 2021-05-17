import random
from qns.topo import Channel
from qns.schedular import Simulator, Protocol, Event
from .event import PhotonReceiveEvent
from qns.log import log

class OpticalFiber(Channel):
    def __init__(self, nodes=[],  name=None):
        self.nodes = nodes

        if name is None:
            self.name = str(id(self))
        else:
            self.name = name

    def __repr__(self):
        return "<bb84 link " + self.name+">"

class OpticalFiberProtocol(Protocol):
    def __init__(_self, entity, delay = 0, possible = 1):
        super().__init__(entity)
        _self.delay = delay
        _self.possible = possible

    def install(_self, simulator: Simulator):
        _self.simulator = simulator
        self = _self.entity
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)
        for n in self.nodes:
            n.links.append(self)

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        self = _self.entity
        new_photon = msg
        if random.random() > _self.possible:
            log.debug("fiber: send photon {} failed", new_photon)
            return

        if len(self.nodes) <= 1:
            log.debug("fiber: break link")
            return
        
        for n in self.nodes:
            if n == source: # do not send back
                continue
            else:
                pre = PhotonReceiveEvent(to = n,new_photon = new_photon, source = source)
                simulator.add_event(simulator.current_time_slice + _self.delay_time_slice, pre)
                return
            