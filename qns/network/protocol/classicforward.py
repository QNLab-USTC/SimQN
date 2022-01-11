from build.lib.qns.entity.cchannel.cchannel import ClassicChannel
from qns.entity.cchannel.cchannel import RecvClassicPacket
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.network.route.route import RouteImpl
from qns.simulator.simulator import Simulator
from qns.simulator.event import Event


class ClassicPacketForwardApp(Application):
    """
    This application will generate routing table for classic networks
    and allow nodes to forward classic packats to the destination.
    """
    def __init__(self, route: RouteImpl):
        """

        Args:
            route (RouteImpl): a route implement
        """
        super().__init__()
        self.route = route

    def install(self, node: QNode, simulator: Simulator):
        super().install(node, simulator)

    def handle(self, node: QNode, event: Event):
        if not isinstance(event, RecvClassicPacket):
            # the event is not receiving a classic packet
            # pass
            return False

        packet = event.packet
        self_node: QNode = self.get_node()

        dst = packet.dest
        if dst == self_node:
            # The destination is this node, return to let later application to handle this packet
            return False

        # If destination is not this node, forward this packet
        route_result = self.route.query(self.get_node(), dst)
        if len(route_result) <= 0 or len(route_result[0]) <= 1:
            # no routing result or error format, drop this packet
            return True
        next_hop = route_result[0][1]
        cchannel: ClassicChannel = self_node.get_cchannel(next_hop)
        if cchannel is None:
            # not found the classic channel, drop the packet
            return True
        cchannel.send(packet=packet, next_hop=next_hop)
        return True
