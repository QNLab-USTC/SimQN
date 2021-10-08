from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import List, Tuple
from qns.network.topology import Topology
import math


class GridTopology(Topology):
    """
    GridTopology includes `nodes_number` Qnodes. `nodes_number` should be a perfect square number.
    The topology is a quare grid pattern, where each node has 4 neighbours.
    """
    def __init__(self, nodes_number):
        super().__init__(nodes_number)
        size = int(math.sqrt(self.nodes_number))
        self.size = size
        assert(size ** 2 == self.nodes_number)

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []

        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(QNode(f"n{i+1}"))
        
        if self.nodes_number > 1:
            for i in range(self.nodes_number):
                if (i + self.size) % self.size != self.size - 1:
                    l = QuantumChannel(name= f"l{i},{i+1}", **self.channel_args)
                    ll.append(l)
                    nl[i].add_qchannel(l)
                    nl[i+1].add_qchannel(l)
                if i + self.size < self.nodes_number:
                    l = QuantumChannel(name= f"l{i},{i+self.size}", **self.channel_args)
                    ll.append(l)
                    nl[i].add_qchannel(l)
                    nl[i+self.size].add_qchannel(l)

        if isinstance(self.nodes_apps, List):
            for n in nl:
                for p in self.nodes_apps:
                    n.add_apps(p)

        return nl,ll
