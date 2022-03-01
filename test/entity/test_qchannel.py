from typing import Any, Optional
from qns.entity.qchannel.losschannel import QubitLossChannel
from qns.simulator.simulator import Simulator
from qns.simulator.event import Event, func_to_event
from qns.simulator.ts import Time
from qns.models.qubit.qubit import Qubit
from qns.entity.node.node import QNode
from qns.entity.qchannel.qchannel import QuantumChannel, RecvQubitPacket
from qns.entity.node.app import Application


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
            time = self._simulator.time(sec=t)
            event = SendEvent(time, node=self, by=self)
            self._simulator.add_event(event)
            t += 0.25

    def send(self):
        print(self._simulator.current_time, "send qubit")
        link: QuantumChannel = self.qchannels[0]
        dest = self.dest
        qubit = Qubit()
        link.send(qubit, dest)


class SendEvent(Event):
    def __init__(self, t: Optional[Time] = None, name: Optional[str] = None, node: QNode = None,
                 by: Optional[Any] = None):
        super().__init__(t=t, name=name, by=by)
        self.node: QuantumSendNode = node

    def invoke(self) -> None:
        self.node.send()


def test_qchannel_first():
    n2 = QuantumRecvNode("n2")
    n1 = QuantumSendNode("n1", dest=n2)
    l1 = QuantumChannel(name="l1", bandwidth=3, delay=0.2, drop_rate=0.1, max_buffer_size=5)
    # l2 = QuantumChannel(name="l2", bandwidth=5, delay=0.5, drop_rate=0.2, max_buffer_size=5)
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)
    s = Simulator(0, 10, 1000)
    n1.install(s)
    n2.install(s)
    s.run()


class SendApp(Application):
    def __init__(self, dest: QNode, qchannel: QuantumChannel, send_rate=1):
        super().__init__()
        self.dest = dest
        self.qchannel = qchannel
        self.send_rate = send_rate

    def install(self, node, simulator: Simulator):
        super().install(node=node, simulator=simulator)
        t = simulator.ts
        event = func_to_event(t, self.send, by=self)
        self._simulator.add_event(event)

    def send(self):
        qubit = Qubit()
        self.qchannel.send(qubit=qubit, next_hop=self.dest)
        t = self._simulator.current_time + self._simulator.time(sec=1 / self.send_rate)
        event = func_to_event(t, self.send, by=self)
        self._simulator.add_event(event)


class RecvApp(Application):
    def handle(self, node, event: Event) -> Optional[bool]:
        if isinstance(event, RecvQubitPacket):
            recv_time = event.t
            print("recv_time:{}".format(recv_time))


def test_qchannel_second():
    n1 = QNode(name="n_1")
    n2 = QNode(name="n_2")
    l1 = QuantumChannel(name="l_1")
    # l2 = QuantumChannel(name="l2", bandwidth=5, delay=0.5, drop_rate=0.2, max_buffer_size=5)
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)
    s = Simulator(1, 5, 1000)
    n1.add_apps(SendApp(dest=n2, qchannel=l1))
    n2.add_apps(RecvApp())
    n1.install(s)
    n2.install(s)
    s.run()


def test_qubit_loss_channel():
    n1 = QNode(name="n_1")
    n2 = QNode(name="n_2")
    l1 = QubitLossChannel(name="loss_channel_1", p_init=0.1, attenuation_rate=0.02, length=100)
    print(l1.drop_rate)
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)
    s = Simulator(1, 5, 1000)
    n1.add_apps(SendApp(dest=n2, qchannel=l1))
    n2.add_apps(RecvApp())
    n1.install(s)
    n2.install(s)
    s.run()
