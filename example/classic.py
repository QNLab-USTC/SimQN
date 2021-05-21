from qns.classic.node import ClassicRecvProtocol, ClassicSendProtocol
from qns.schedular.protocol import Protocol
from qns.schedular import Simulator, Protocol
from qns.classic import ClassicNode, ClassicLink, ClassicLinkProtocol, Message
from qns.log import log

class SendTimeProtocol(Protocol):
    def __init__(_self, entity, link ,start_time, end_time, step_time, message = "Ping"):
        super().__init__(entity)
        _self.start_time = start_time
        _self.end_time = end_time
        _self.step_time = step_time
        _self.link = link
        _self.message = message

    def install(_self, simulator: Simulator):
        self = _self.entity
        _self.simulator = simulator
        _self.start_time_slice = simulator.to_time_slice(_self.start_time)
        _self.end_time_slice = simulator.to_time_slice(_self.end_time)
        _self.step_time_slice = simulator.to_time_slice(_self.step_time)
        msg = Message(_self.message)

        for i in range(_self.start_time_slice, _self.end_time_slice, _self.step_time_slice):
            self.call(simulator, (_self.link, msg), source = self, event = None, time_slice = i)

s = Simulator(0, 10, 100000)
log.install(s)
log.set_debug(True)

n1 = ClassicNode("n1")
nsp1 = ClassicSendProtocol(n1)
n1.inject_protocol(nsp1)

n2 = ClassicNode("n2")
nrp2 = ClassicRecvProtocol(n2)
n2.inject_protocol(nrp2)


l1 = ClassicLink(nodes = [n1, n2], name = "l1")
clp = ClassicLinkProtocol(l1, delay = 0.2, possible = 0.99, rate = 20)
l1.inject_protocol(clp)
l1.install(s)

stp = SendTimeProtocol(n1, l1, 1, 10, 0.1)
n1.inject_protocol(stp)
n1.install(s)
n2.install(s)

s.run()
