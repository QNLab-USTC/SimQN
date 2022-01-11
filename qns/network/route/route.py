
from typing import List, Tuple, Union
from qns.entity import QNode
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.cchannel.cchannel import ClassicChannel


class NetworkRouteError(Exception):
    pass


class RouteImpl():
    """
    This is the route protocol interface
    """

    def __init__(self, name: str = "route") -> None:
        self.name = name

    def build(self, nodes: List[QNode], channels: List[Union[QuantumChannel, ClassicChannel]]):
        """
        build static route tables for each nodes

        args:
            channels: a list of quantum channels or classic channels
        """
        raise NotImplementedError

    def query(self, src: QNode, dest: QNode) -> List[Tuple[float, QNode, List[QNode]]]:
        """
        query the metric, nexthop and the path

        Args:
            src: the source node
            dest: the destination node

        Returns:
            A list of route paths. The result should be sortted by the priority.
            The element is a tuple containing: metric, the next-hop and the whole path.
        """
        raise NotImplementedError
