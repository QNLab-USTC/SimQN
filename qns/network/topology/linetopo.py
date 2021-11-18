from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import Dict, List, Optional, Tuple
from qns.network.topology import Topology


class LineTopology(Topology):
    """
    LineTopology includes `nodes_number` Qnodes. The topology is a line pattern.
    """
    def __init__(self, nodes_number, nodes_apps: List[Application] = [], qchannel_args: Dict = {}, cchannel_args: Dict = {}, memory_args: Optional[List[Dict]] = {}):
        super().__init__(nodes_number, nodes_apps=nodes_apps, qchannel_args = qchannel_args, cchannel_args = cchannel_args, memory_args= memory_args)

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []
        if self.nodes_number >= 1:
            n = QNode(f"n{1}")
            nl.append(n)
        pn = n
        for i in range(self.nodes_number - 1):
            n = QNode(f"n{i+2}")
            nl.append(n)
            l = QuantumChannel(name= f"l{i+1}", **self.qchannel_args)
            ll.append(l)

            pn.add_qchannel(l)
            n.add_qchannel(l)
            pn = n

        self._add_apps(nl)
        self._add_memories(nl)
        return nl,ll
