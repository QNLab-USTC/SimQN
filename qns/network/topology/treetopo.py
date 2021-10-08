from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import List, Tuple
from qns.network.topology import Topology


class TreeTopology(Topology):
    """
    TreeTopology includes `nodes_number` Qnodes. The topology is a tree pattern, where each parent has `children_num` children.
    """
    def __init__(self, nodes_number, children_number: int = 2):
        """
        Args:
            nodes_number (int): the total number of QNodes
            children_number (int): the number of children one parent has
        """
        super().__init__(nodes_number)
        self.children_number = children_number

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []

        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(QNode(f"n{i+1}"))

        for i in range(self.nodes_number):
            for j in range(i * self.children_number + 1, (i+1) * self.children_number + 1):
                if j < self.nodes_number:
                    l = QuantumChannel(name= f"l{i},{j}", **self.channel_args)
                    ll.append(l)
                    nl[i].add_qchannel(l)
                    nl[j].add_qchannel(l)

        if isinstance(self.nodes_apps, List):
            for n in nl:
                for p in self.nodes_apps:
                    n.add_apps(p)

        return nl,ll
