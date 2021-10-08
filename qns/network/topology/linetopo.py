from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import List, Tuple
from qns.network.topology import Topology


class LineTopology(Topology):
    """
    LineTopology includes `nodes_number` Qnodes. The topology is a line pattern.
    """
    def __init__(self, nodes_number):
        super().__init__(nodes_number)

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []
        if self.nodes_number >= 1:
            n = QNode(f"n{1}")
        nl.append(n)
        pn = n
        for i in range(self.nodes_number - 1):
            n = QNode(f"n{i+2}")
            nl.append(QNode(f"n{i+2}"))
            l = QuantumChannel(name= f"l{i+1}", **self.channel_args)
            ll.append(l)

            pn.add_qchannel(l)
            n.add_qchannel(l)
            pn = n

        if isinstance(self.nodes_apps, List):
            for n in nl:
                for p in self.nodes_apps:
                    n.add_apps(p)

        return nl,ll
