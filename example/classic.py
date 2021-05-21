from qns.classic.node import ClassicRecvProtocol, ClassicSendProtocol, ClassicSwitchProtocol
from qns.schedular.protocol import Protocol
from qns.schedular import Simulator, Protocol
from qns.classic import ClassicNode, ClassicLink, ClassicLinkProtocol, Message
from qns.log import log

class SendTimeProtocol(Protocol):
    def __init__(_self, entity, from_node, to_node, link ,start_time, end_time, step_time, message = "Ping"):
        super().__init__(entity)
        _self.start_time = start_time
        _self.end_time = end_time
        _self.step_time = step_time
        _self.link = link
        _self.from_node = from_node
        _self.to_node = to_node
        _self.message = message


    def install(_self, simulator: Simulator):
        self = _self.entity
        _self.simulator = simulator
        _self.start_time_slice = simulator.to_time_slice(_self.start_time)
        _self.end_time_slice = simulator.to_time_slice(_self.end_time)
        _self.step_time_slice = simulator.to_time_slice(_self.step_time)

        # for i in range(_self.start_time_slice, _self.end_time_slice, _self.step_time_slice):
        msg = Message(_self.message, _self.from_node, _self.to_node, _self.link)
        self.call(simulator, msg, source = self, event = None, time_slice = _self.start_time_slice)

s = Simulator(0, 10, 100000)
log.install(s)
log.set_debug(True)

n1 = ClassicNode("n1")
nsp1 = ClassicSendProtocol(n1)
n1.inject_protocol(nsp1)

n2 = ClassicNode("n2")
nrp2 = ClassicRecvProtocol(n2)
n2.inject_protocol(nrp2)

n3 = ClassicNode("s1")

l1 = ClassicLink(nodes = [n1, n3], name = "l1")
clp1 = ClassicLinkProtocol(l1, delay = 0.2, possible = 0.99, rate = 20)
l1.inject_protocol(clp1)
l1.install(s)

l2 = ClassicLink(nodes = [n3, n2], name = "l2")
clp2 = ClassicLinkProtocol(l2, delay = 0.2, possible = 0.99, rate = 20)
l2.inject_protocol(clp2)
l2.install(s)

stp = SendTimeProtocol(entity= n1, link = l1,from_node= n1, to_node= n2, start_time = 1, end_time = 10, step_time = 0.1)
n1.inject_protocol(stp)

nsp = ClassicSwitchProtocol(n3, forwarding={n1:l1, n2: l2}, delay = 0.1)
n3.inject_protocol(nsp)

n1.install(s)
n2.install(s)
n3.install(s)


s.run()
