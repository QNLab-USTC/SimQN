from qns.entity.node.app import Application
from typing import Dict, List, Tuple
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode


class Topology(object):
    """
    Topology is a factory for QuantumNetwork
    """

    def __init__(self, nodes_number: int, nodes_apps: List[Application] = [], channel_args: Dict = {}):
        """
        Args:
            nodes_number: the number of Qnodes
        """
        self.nodes_number = nodes_number
        self.nodes_apps = nodes_apps
        self.channel_args = channel_args

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        """
        build the special topology

        Returns:
            the list of QNodes and the list of QuantumChannel
        """
        pass
