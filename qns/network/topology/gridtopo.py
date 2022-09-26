#    SimQN: a discrete-event simulator for the quantum networks
#    Copyright (C) 2021-2022 Lutong Chen, Jian Li, Kaiping Xue
#    University of Science and Technology of China, USTC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from typing import Dict, List, Optional, Tuple
from qns.network.topology import Topology
import math


class GridTopology(Topology):
    """
    GridTopology includes `nodes_number` Qnodes. `nodes_number` should be a perfect square number.
    The topology is a square grid pattern, where each node has 4 neighbors.
    """
    def __init__(self, nodes_number, nodes_apps: List[Application] = [],
                 qchannel_args: Dict = {}, cchannel_args: Dict = {},
                 memory_args: Optional[List[Dict]] = {}):
        super().__init__(nodes_number, nodes_apps, qchannel_args, cchannel_args, memory_args)
        size = int(math.sqrt(self.nodes_number))
        self.size = size
        assert (size ** 2 == self.nodes_number)

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []

        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(n)

        if self.nodes_number > 1:
            for i in range(self.nodes_number):
                if (i + self.size) % self.size != self.size - 1:
                    link = QuantumChannel(name=f"l{i},{i+1}", **self.qchannel_args)
                    ll.append(link)
                    nl[i].add_qchannel(link)
                    nl[i + 1].add_qchannel(link)
                if i + self.size < self.nodes_number:
                    link = QuantumChannel(name=f"l{i},{i+self.size}", **self.qchannel_args)
                    ll.append(link)
                    nl[i].add_qchannel(link)
                    nl[i + self.size].add_qchannel(link)

        self._add_apps(nl)
        self._add_memories(nl)
        return nl, ll
