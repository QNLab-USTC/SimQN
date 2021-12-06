
from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import Dict, List, Optional, Tuple
from qns.network.topology import Topology

import random
import itertools
import numpy as np


class WaxmanTopology(Topology):
    """
    WaxmanTopology is the random topology generator using Waxman's model.
    """
    def __init__(self, nodes_number: int, size: float, alpha: float, beta: float,
                 nodes_apps: List[Application] = [],
                 qchannel_args: Dict = {}, cchannel_args: Dict = {},
                 memory_args: Optional[List[Dict]] = {}):
        """
        Args:
            nodes_number (int): the number of Qnodes
            size (float): the area size (meter)
            alpha (float): alpha parameter in Waxman's model
            beta (float): alpha parameter in Waxman's model
        """
        super().__init__(nodes_number, nodes_apps, qchannel_args, cchannel_args, memory_args)
        self.size = size
        self.alpha = alpha
        self.beta = beta

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll: List[QuantumChannel] = []

        location_table: Dict[QNode, Tuple[float, float]] = {}
        distance_table: Dict[Tuple[QNode, QNode], float] = {}

        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(n)
            x = random.random() * self.size
            y = random.random() * self.size
            location_table[n] = (x, y)

        L = 0
        cb = list(itertools.combinations(nl, 2))
        for n1, n2 in cb:
            tmp_l = np.sqrt((location_table[n1][0] - location_table[n2][0]) ** 2 +
                            (location_table[n1][1] - location_table[n2][1]) ** 2)
            distance_table[(n1, n2)] = tmp_l
            if tmp_l > L:
                L = tmp_l

        for n1, n2 in cb:
            if n1 == n2:
                continue
            d = distance_table[(n1, n2)]
            p = self.alpha * np.exp(-d / (self.beta * L))
            if random.random() < p:
                link = QuantumChannel(name=f"l{n1}-{n2}", length=d, **self.qchannel_args)
                ll.append(link)
                n1.add_qchannel(link)
                n2.add_qchannel(link)
        self._add_apps(nl)
        self._add_memories(nl)
        return nl, ll
