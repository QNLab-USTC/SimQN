from typing import Optional
from qns.simulator.simulator import Simulator
from qns.simulator.event import Event
from qns.simulator.ts import Time
from qns.entity.node.node import QNode
from qns.entity.cchannel.cchannel import ClassicChannel, ClassicPacket, RecvClassicPacket


class ClassicRecvNode(QNode):
    def handle(self, event: Event) -> None:
        if isinstance(event, RecvClassicPacket):
            print(event.t, event.packet.src, event.packet.dest, event.packet.msg)


class ClassicSendNode(QNode):
    def __init__(self, name: str = None, dest: QNode = None):
        super().__init__(name=name)
        self.dest = dest

    def install(self, simulator: Simulator) -> None:
        super().install(simulator)

        t = 0
        while t < 10:
            time = self._simulator.time(sec=t)
            event = SendEvent(time, node=self)
            self._simulator.add_event(event)
            t += 0.25

    def send(self):
        print(self._simulator.current_time, "send packet")
        link: ClassicChannel = self.cchannels[0]
        dest = self.dest
        packet = ClassicPacket(msg="ping", src=self, dest=dest)
        link.send(packet, dest)


class SendEvent(Event):
    def __init__(self, t: Optional[Time] = None, name: Optional[str] = None, node: QNode = None):
        super().__init__(t=t, name=name)
        self.node: ClassicSendNode = node

    def invoke(self) -> None:
        self.node.send()


n2 = ClassicRecvNode("n2")
n1 = ClassicSendNode("n1", dest=n2)
l1 = ClassicChannel(name="l1", bandwidth=10, delay=0.2, drop_rate=0.1, max_buffer_size=30)
n1.add_cchannel(l1)
n2.add_cchannel(l1)

s = Simulator(0, 10, 1000)
n1.install(s)
n2.install(s)
s.run()
