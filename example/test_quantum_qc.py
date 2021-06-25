from qns.quantum.entity.quantum_channel import QuantumChannel
from qns.quantum.protocol.protocol import NodeProtocol
from qns.quantum.entity import Node
from qns.quantum.entity import QuantumChannel, QuantumChannelReceiveEvent, QuantumChannelSendEvent
from qns.quantum.qubit import Qubit, Polar
from qns.schedular import Simulator, Protocol
from qns.log import log

class SendQubitProtocol(Protocol):
    def __init__(_self, entity, from_node, to_node, link ,start_time, end_time, step_time):
        super().__init__(entity)
        _self.start_time = start_time
        _self.end_time = end_time
        _self.step_time = step_time
        _self.link: QuantumChannel = link
        _self.from_node = from_node
        _self.to_node = to_node


    def install(_self, simulator: Simulator):
        self = _self.entity

        _self.simulator = simulator
        _self.start_time_slice = simulator.to_time_slice(_self.start_time)
        _self.end_time_slice = simulator.to_time_slice(_self.end_time)
        _self.step_time_slice = simulator.to_time_slice(_self.step_time)

        for i in range(_self.start_time_slice, _self.end_time_slice, _self.step_time_slice):
            q = Qubit(fidelity= 1, birth_time_slice= simulator.current_time_slice)
            q.polar = Polar.A
            se = QuantumChannelSendEvent(qubit = q, source = _self.from_node)

            _self.link.call(simulator, msg = None , source= _self.entity, event = se, time_slice = i)



class RecvQubitProtocol(NodeProtocol):
    def run(_self, simulator: Simulator):
        while True:
            (msg, source, event) =  yield None
            if not isinstance(event, QuantumChannelReceiveEvent):
                continue

            qubit = event.qubit
            source = event.source
            log.info(f"{_self.entity} recv qubit {qubit} from {source}")


s = Simulator(0, 10, 1000)
log.install(s)
log.set_debug(True)

n1 = Node("n1")
n2 = Node("n2")

l1 = QuantumChannel("l1", delay = 0.233, loss_rate= 0.5, bandwidth= 3)
l1.add_nodes(n1, n2)

nsp = SendQubitProtocol(n1, n1, n2, l1, 1, 8, 0.2)
nrp = RecvQubitProtocol(n2)

n1.inject_protocol(nsp)
n2.inject_protocol(nrp)

n1.install(s)
n2.install(s)
l1.install(s)

s.run()
