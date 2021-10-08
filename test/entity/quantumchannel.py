import logging
from typing import Optional
from qns import Event, Time, Simulator, log
from qns.models.qubit import Qubit
from qns.entity import QNode, QuantumChannel, RecvQubitPacket

log.setLevel(logging.DEBUG)

class QuantumRecvNode(QNode):
    def handle(self, event: Event) -> None:
        if isinstance(event, RecvQubitPacket):
            print(event.t, event.qubit)

class QuantumSendNode(QNode):
    def __init__(self, name: str = None, dest: QNode = None):
        super().__init__(name=name)
        self.dest = dest

    def install(self, simulator: Simulator) -> None:
        super().install(simulator)

        t = 0
        while t < 10:
            time = self._simulator.time(sec = t)
            event = SendEvent(time, node = self)
            self._simulator.add_event(event)
            t += 0.25

    def send(self):
        print(self._simulator.current_time, "send qubit")
        link: QuantumChannel = self.qchannels[0]
        dest = self.dest
        qubit = Qubit()
        link.send(qubit, dest)
        
class SendEvent(Event):
    def __init__(self, t: Optional[Time] = None, name: Optional[str] = None, node: QNode = None):
        super().__init__(t=t, name=name)
        self.node: QuantumSendNode = node
        
    def invoke(self) -> None:
        self.node.send()

n2 = QuantumRecvNode("n2")
n1 = QuantumSendNode("n1", dest = n2)
l1 = QuantumChannel(name="l1", bandwidth= 3, delay = 0.2, drop_rate= 0.1, max_buffer_size=5)

n1.add_qchannel(l1)
n2.add_qchannel(l1)
s = Simulator(0, 10, 1000)
n1.install(s)
n2.install(s)
s.run()


