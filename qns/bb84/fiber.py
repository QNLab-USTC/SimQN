import random
from qns.topo import Channel
from qns.schedular import Simulator, Protocol, Event
from .event import PhotonReceiveEvent
from qns.log import log
import uuid


class OpticalFiber(Channel):
    def __init__(self, nodes=[],  name=None):
        self.nodes = nodes

        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

    def __repr__(self):
        return "<bb84 link " + self.name+">"


class OpticalFiberProtocol(Protocol):
    def __init__(_self, entity, delay=0, possible=1, rate=None, max_onfly=None):
        super().__init__(entity)
        _self.delay = delay
        _self.possible = possible
        _self.rate = rate
        _self.max_onfly = max_onfly

    def install(_self, simulator: Simulator):
        _self.simulator = simulator
        self = _self.entity
        _self.current_token = simulator.start_time_slice
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)
        if _self.rate is not None:
            _self.step_time_slice = int(simulator.time_accuracy / _self.rate)
        else:
            _self.step_time_slice = None

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

        send_time_slice = simulator.current_time_slice
        if _self.step_time_slice is not None:
            if simulator.current_time_slice > _self.current_token:
                send_time_slice = simulator.current_time_slice
                _self.current_token = simulator.current_time_slice + _self.step_time_slice
            else:
                if _self.max_onfly is not None and (_self.current_token - simulator.current_time_slice) / _self.step_time_slice > _self.max_onfly:
                    log.debug(f"fiber {self.name}: drop message")
                    return
                send_time_slice = _self.current_token
                _self.current_token = _self.current_token + _self.step_time_slice

        for n in self.nodes:
            if n == source:  # do not send back
                continue
            else:
                pre = PhotonReceiveEvent(
                    to=n, new_photon=new_photon, source=source)
                simulator.add_event(
                    send_time_slice + _self.delay_time_slice, pre)
                return
