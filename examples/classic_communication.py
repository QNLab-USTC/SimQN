
from qns.simulator.simulator import Simulator
from qns.simulator.event import Event
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.entity.cchannel.cchannel import ClassicChannel, ClassicPacket, RecvClassicPacket
from qns.simulator import func_to_event


# the send application
class SendApp(Application):
    def __init__(self, dest: QNode, cchannel: ClassicChannel, send_rate=1):
        super().__init__()
        self.dest = dest
        self.cchannel = cchannel
        self.send_rate = send_rate

    # initiate: generate the first send event
    def install(self, node: QNode, simulator: Simulator):
        super().install(node, simulator)

        # get start time

        t = simulator.ts
        event = func_to_event(t, self.send_packet, by=self)
        self._simulator.add_event(event)

    def send_packet(self):
        # generate a packet
        packet = ClassicPacket(msg="Hello,world", src=self.get_node(), dest=self.dest)

        # send the classic packet
        self.cchannel.send(packet=packet, next_hop=self.dest)

        # calculate the next sending time
        t = self._simulator.current_time + \
            self._simulator.time(sec=1 / self.send_rate)

        # insert the next send event to the simulator
        event = func_to_event(t, self.send_packet, by=self)
        self._simulator.add_event(event)


class RecvApp(Application):
    def __init__(self):
        super().__init__()
        self.add_handler(self.handleClassicPacket, [RecvClassicPacket], [])

    def handleClassicPacket(self, node: QNode, event: Event):
        if isinstance(event, RecvClassicPacket):
            packet = event.packet

            # get the packet message
            msg = packet.get()

            # handling the receiving packet
            # ...
            print(msg)


# generate quantum nodes
n1 = QNode("n1")
n2 = QNode("n2")

# generate a classic channel
l1 = ClassicChannel(name="l1")
n1.add_cchannel(l1)
n2.add_cchannel(l1)

# add apps
n1.add_apps(SendApp(dest=n2, cchannel=l1))
n2.add_apps(RecvApp())


s = Simulator(0, 10, 10000)
n1.install(s)
n2.install(s)

# run the simulation
s.run()
