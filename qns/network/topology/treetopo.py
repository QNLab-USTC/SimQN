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


class TreeTopology(Topology):
    """
    TreeTopology includes `nodes_number` Qnodes.
    The topology is a tree pattern, where each parent has `children_num` children.
    """
    def __init__(self, nodes_number, children_number: int = 2, nodes_apps: List[Application] = [],
                 qchannel_args: Dict = {}, cchannel_args: Dict = {},
                 memory_args: Optional[List[Dict]] = {}):
        """
        Args:
            nodes_number (int): the total number of QNodes
            children_number (int): the number of children one parent has
        """
        super().__init__(nodes_number, nodes_apps, qchannel_args, cchannel_args, memory_args)
        self.children_number = children_number

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []

        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(n)

        for i in range(self.nodes_number):
            for j in range(i * self.children_number + 1, (i + 1) * self.children_number + 1):
                if j < self.nodes_number:
                    link = QuantumChannel(name=f"l{i},{j}", **self.qchannel_args)
                    ll.append(link)
                    nl[i].add_qchannel(link)
                    nl[j].add_qchannel(link)

        self._add_apps(nl)
        self._add_memories(nl)
        return nl, ll
