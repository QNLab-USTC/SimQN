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
from qns.network.topology.topo import Topology


class BasicTopology(Topology):
    """
    BasicTopology includes `nodes_number` Qnodes. None of them are connected with each other
    """
    def __init__(self, nodes_number, nodes_apps: List[Application] = [],
                 qchannel_args: Dict = {}, cchannel_args: Dict = {},
                 memory_args: Optional[List[Dict]] = {}):
        super().__init__(nodes_number, nodes_apps, qchannel_args, cchannel_args, memory_args)

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        nl: List[QNode] = []
        ll = []
        for i in range(self.nodes_number):
            n = QNode(f"n{i+1}")
            nl.append(n)

        self._add_apps(nl)
        self._add_memories(nl)
        return nl, ll
