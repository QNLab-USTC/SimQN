
from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import Dict, List, Optional, Tuple
from qns.network.topology import Topology

import numpy as np
import random


class RandomTopology(Topology):
    """
    RandomTopology includes `nodes_number` Qnodes. The topology is randomly generated.
    """
    def __init__(self, nodes_number, lines_number: int, nodes_apps: List[Application] = [], qchannel_args: Dict = {}, cchannel_args: Dict = {}, memory_args: Optional[List[Dict]] = {}):
        """
        Args:
            nodes_number: the number of Qnodes
            lines_number: the number of lines (QuantumChannel)
        """
        super().__init__(nodes_number, nodes_apps, qchannel_args, cchannel_args, memory_args)
        self.lines_number = lines_number

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll: List[QuantumChannel] = []

        mat = [[0 for i in range(self.nodes_number)] for j in range(self.nodes_number)]

        if self.nodes_number >= 1:
            n = QNode(f"n{1}")
            nl.append(n)
        
        for i in range(self.nodes_number - 1):
            n = QNode(f"n{i+2}")
            nl.append(n)
            
            idx = random.randint(0,i)
            pn = nl[idx]
            mat[idx][i+1] = 1
            mat[i+1][idx] = 1

            l = QuantumChannel(name= f"l{idx+1},{i+2}", **self.qchannel_args)
            ll.append(l)
            pn.add_qchannel(l)
            n.add_qchannel(l)

        if self.lines_number > self.nodes_number - 1:
            for i in range(self.nodes_number - 1, self.lines_number):
                while True:
                    a = random.randint(0, self.nodes_number - 1)
                    b = random.randint(0, self.nodes_number - 1)
                    if mat[a][b] == 0:
                        break
                mat[a][b] = 1
                mat[b][a] = 1
                n = nl[a]
                pn = nl[b]
                l = QuantumChannel(name= f"l{a+1},{b+1}", **self.qchannel_args)
                ll.append(l)
                pn.add_qchannel(l)
                n.add_qchannel(l)

        self._add_apps(nl)
        self._add_memories(nl)
        return nl,ll
