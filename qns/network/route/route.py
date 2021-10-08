
from typing import List, Tuple
from qns.entity import QNode
from qns.entity.qchannel.qchannel import QuantumChannel

class NetworkRouteError(Exception):
    pass

class RouteImpl():
    """
    This is the route protocol interface
    """

    def __init__(self, name: str = "route") -> None:
        self.name = name

    def build(self, nodes: List[QNode], qchannels: List[QuantumChannel]):
        """
        build static route tables for each nodes
        """
        raise NotImplemented

    def query(self, src: QNode, dest: QNode) -> List[Tuple[float, QNode, List[QNode]]]:
        """
        query the metric, nexthop and the path

        Args:
            src: the source node
            dest: the destination node
        
        Returns:
            A list of route paths. The result should be sortted by the perority.
            The element is a tuple containing: metric, the next-hop and the whole path.
        """
        raise NotImplemented