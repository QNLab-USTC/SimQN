from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import List, Tuple
from qns.network.topology.topo import Topology

class BasicTopology(Topology):
    """
    BasicTopology includes `nodes_number` Qnodes. None of them are connected with each other
    """
    def __init__(self, nodes_number):
        super().__init__(nodes_number)

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []
        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(n)
        if isinstance(self.nodes_apps, List):
            for n in nl:
                for p in self.nodes_apps:
                    n.add_apps(p)
        return nl,ll