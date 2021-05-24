import random
from qns.topo import Channel
from qns.schedular import Simulator, Protocol, Event
from .event import PhotonReceiveEvent
from qns.log import log


class OpticalFiber(Channel):
    '''
    The quantum optical fiber to tranfer a photon.

    :param nodes: quantum nodes that it is attached to
    :param str name: its name
    '''
    def __init__(self, nodes=[],  name=None):
        super().__init__(name)
        self.nodes = nodes

    def __repr__(self):
        return "<bb84 link " + self.name+">"


class OpticalFiberProtocol(Protocol):
    '''
    The protocol for optical fiber. It transfer a photon from one side to another.

    :param entity: a quantum optical fiber
    :param delay: its delay time in second
    :param possible: its transmission success rate
    :param rate: how many photon it can transfer per second
    :param max_onfly: how many photon it can cached for sending. Over this bound, the new coming photon will be dropped.
    '''
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
        '''
        Transmit a photon in `msg` and send it to another node.

        :param simulator: the simulator
        :param msg: the sending photon
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
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
