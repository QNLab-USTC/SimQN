from typing import Optional
from qns.entity.monitor.monitor import Monitor
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.entity.qchannel.qchannel import QuantumChannel, RecvQubitPacket
from qns.models.qubit.qubit import Qubit
from qns.simulator.event import func_to_event, Event
from qns.simulator.simulator import Simulator


class SendApp(Application):
    def __init__(self, dest: QNode, qchannel: QuantumChannel, send_rate=1):
        super().__init__()
        self.dest = dest
        self.qchannel = qchannel
        self.send_rate = send_rate
        self.count = 0

    def install(self, node, simulator: Simulator):
        super().install(node=node, simulator=simulator)
        t = simulator.ts
        event = func_to_event(t, self.send, by=self)
        self._simulator.add_event(event)

    def send(self):
        qubit = Qubit()
        self.qchannel.send(qubit=qubit, next_hop=self.dest)
        self.count += 1
        t = self._simulator.current_time + self._simulator.time(sec=1 / self.send_rate)
        event = func_to_event(t, self.send, by=self)
        self._simulator.add_event(event)


class RecvApp(Application):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.add_handler(self.RecvQubitHandler, [RecvQubitPacket])

    def RecvQubitHandler(self, node, event: Event) -> Optional[bool]:
        self.count += 1


def test_monitor_1():
    n1 = QNode(name="n_1")
    n2 = QNode(name="n_2")
    # l1 = QuantumChannel(name="l_1")
    l1 = QuantumChannel(name="l1", bandwidth=5, delay=0.5, drop_rate=0.2, max_buffer_size=5)
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)
    s = Simulator(0, 10, 1000)
    sp = SendApp(dest=n2, qchannel=l1, send_rate=3)
    rp = RecvApp()
    n1.add_apps(sp)
    n2.add_apps(rp)
    n1.install(s)
    n2.install(s)

    m = Monitor()

    def watch_send_count(simulator, network, event):
        return sp.count

    def watch_recv_count(simulator, network, event):
        return rp.count

    m.add_attribution(name="send_count", calculate_func=watch_send_count)
    m.add_attribution(name="recv_count", calculate_func=watch_recv_count)
    m.add_attribution(name="event_name", calculate_func=lambda s, n, e: e.__class__)

    m.at_start()
    m.at_finish()
    m.at_period(period_time=1)
    m.at_event(RecvQubitPacket)
    m.install(s)
    s.run()
    print(m.get_date())


if __name__ == "__main__":
    test_monitor_1()
