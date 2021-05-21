from qns.topo import Node
from qns.schedular import Protocol, Simulator, Event
from .event import GenerationAndSendEvent, PhotonReceiveEvent
from .photon import Photon, Basis, Polar
from qns.log import log
import uuid


class PhotonNode(Node):
    def __init__(self, registers_number: int = -1, name=None):
        self.links = []

        self.registers_number = registers_number
        self.registers = []

        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

    def __repr__(self):
        return "<bb84 node " + self.name+">"


class PhotonRandomSendProtocol(Protocol):
    def __init__(_self, entity, rate=1, start_time=None, end_time=None):
        super().__init__(entity)
        _self.rate = rate
        _self.start_time = start_time
        _self.end_time = end_time

    def install(_self, simulator: Simulator):
        _self.simulator = simulator
        if _self.start_time is None:
            _self.start_time_slice = simulator.start_time_slice
        else:
            _self.start_time_slice = simulator.to_time_slice(_self.start_time)

        if _self.end_time is None:
            _self.end_time_slice = simulator.end_time_slice
        else:
            _self.end_time_slice = simulator.to_time_slice(_self.end_time)
        _self.step_time_slice = int(simulator.time_accuracy / _self.rate)

        for i in range(_self.start_time_slice, _self.end_time_slice, _self.step_time_slice):
            gse = GenerationAndSendEvent(
                _self, _self.entity, simulator.current_time)
            simulator.add_event(i, gse)

    def run(_self, simulator: Simulator, event: Event):
        self = _self.entity
        new_photon = Photon()
        new_photon.random_preparation()
        if len(self.links) <= 0:
            log.debug("no link attached on {}", self)
            return
        log.debug("{} send {} on {}", self, new_photon, self.links[0])
        self.links[0].call(simulator, new_photon, source=self, event=event)

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        pass


class PhotonReceiveAndMeasureProtocol(Protocol):
    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        self = _self.entity
        if not isinstance(event, PhotonReceiveEvent):
            return
        new_photon = msg
        source = source
        basis, polar = new_photon.random_measure()
        log.debug("{} recv photon from {}.Use {} measure: {}",
                  self, source, basis, polar)
