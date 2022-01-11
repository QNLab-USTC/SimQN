from qns.entity.cchannel.cchannel import ClassicChannel, ClassicPacket, RecvClassicPacket
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.network.network import QuantumNetwork
from qns.network.protocol.classicforward import ClassicPacketForwardApp
from qns.network.route.dijkstra import DijkstraRouteAlgorithm
from qns.network.route.route import RouteImpl
from qns.network.topology.linetopo import LineTopology
from qns.network.topology.topo import ClassicTopology
from qns.simulator.event import Event, func_to_event
from qns.simulator.simulator import Simulator


class SendApp(Application):
    def __init__(self, dest: QNode, route: RouteImpl, send_rate=1):
        super().__init__()
        self.dest = dest
        self.route = route
        self.send_rate = send_rate

    def install(self, node: QNode, simulator: Simulator):
        super().install(node, simulator)
        t = simulator.ts
        event = func_to_event(t, self.send_packet)
        self._simulator.add_event(event)

    def send_packet(self):
        packet = ClassicPacket(msg=f"Hello,world from {self.get_node()}", src=self.get_node(), dest=self.dest)

        route_result = self.route.query(self.get_node(), self.dest)
        if len(route_result) <= 0 or len(route_result[0]) <= 1:
            print("not found next hop")
        next_hop = route_result[0][1]
        cchannel: ClassicChannel = self.get_node().get_cchannel(next_hop)
        if cchannel is None:
            print("not found next channel")

        # send the classic packet
        cchannel.send(packet=packet, next_hop=next_hop)

        # calculate the next sending time
        t = self._simulator.current_time + \
            self._simulator.time(sec=1 / self.send_rate)

        # insert the next send event to the simulator
        event = func_to_event(t, self.send_packet)
        self._simulator.add_event(event)


# the receiving application
class RecvApp(Application):
    def handle(self, node: QNode, event: Event):
        if isinstance(event, RecvClassicPacket):
            packet = event.packet
            msg = packet.get()
            print(f"{node} recv packet: {msg} from {packet.src}->{packet.dest}")


def main():
    s = Simulator(0, 10, accuracy=10000000)

    topo = LineTopology(nodes_number=10,
                        qchannel_args={"delay": 0.1},
                        cchannel_args={"delay": 0.1})

    net = QuantumNetwork(topo=topo, classic_topo=ClassicTopology.Follow)

    # build quantum routing table
    net.build_route()

    classic_route = DijkstraRouteAlgorithm(name="classic route")

    # build classic routing table
    classic_route.build(net.nodes, net.cchannels)
    print(classic_route.route_table)

    for n in net.nodes:
        n.add_apps(ClassicPacketForwardApp(classic_route))
        n.add_apps(RecvApp())

    n1 = net.get_node("n1")
    n10 = net.get_node("n10")

    n1.add_apps(SendApp(n10, classic_route))

    net.install(s)
    s.run()


if __name__ == "__main__":
    main()
