from qns.classic import message
from qns.quantum.protocol.protocol import NodeProtocol
from qns.quantum.entity import Node
from qns.quantum.entity import ClassicChannel, ClassicTransferEvent
from qns.schedular import Simulator, Protocol
from qns.log import log

class SendMessageProtocol(Protocol):
    def __init__(_self, entity, from_node, to_node, link ,start_time, end_time, step_time, message = "Ping"):
        super().__init__(entity)
        _self.start_time = start_time
        _self.end_time = end_time
        _self.step_time = step_time
        _self.link: ClassicChannel = link
        _self.from_node = from_node
        _self.to_node = to_node
        _self.message = message


    def install(_self, simulator: Simulator):
        self = _self.entity
        _self.simulator = simulator
        _self.start_time_slice = simulator.to_time_slice(_self.start_time)
        _self.end_time_slice = simulator.to_time_slice(_self.end_time)
        _self.step_time_slice = simulator.to_time_slice(_self.step_time)

        for i in range(_self.start_time_slice, _self.end_time_slice, _self.step_time_slice):
            _self.link.call(simulator, _self.message, _self.from_node, ClassicTransferEvent(), i)

class RecvMessageProtocol(NodeProtocol):
    def run(_self, simulator: Simulator):
        while True:
            (msg, source, event) =  yield None
            print(_self.entity, "recv message:",msg)


s = Simulator(0, 10, 1000)
log.install(s)
log.set_debug(True)

n1 = Node("n1")
n2 = Node("n2")

l1 = ClassicChannel("l1", 0.02, 0.8, 20)
l1.add_nodes(n1, n2)

nsp = SendMessageProtocol(n1, n1, n2, l1, 1, 8, 0.2)
nrp = RecvMessageProtocol(n2)

n1.inject_protocol(nsp)
n2.inject_protocol(nrp)

n1.install(s)
n2.install(s)
l1.install(s)

s.run()
