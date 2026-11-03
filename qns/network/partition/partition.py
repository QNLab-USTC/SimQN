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

from abc import ABC, abstractmethod
from typing import Dict, List

from qns.entity.node.node import QNode


class Partitioner(ABC):
    """
    Abstract class for partitioning a list of QNodes across MPI ranks.
    """

    @abstractmethod
    def partition(self, nodes: List[QNode], num_ranks: int) -> Dict[str, int]:
        """
        Partition QNodes across ranks.

        Args:
            nodes: the full list of QNodes in the topology
            num_ranks: total number of MPI processes (ranks)

        Returns:
            a mapping from node name to rank index
        """
        pass


class ManualPartitioner(Partitioner):
    """
    Partition QNodes using a manually specified mapping.
    """

    def __init__(self, mapping: Dict[str, int]):
        """
        Args:
            mapping: e.g. {"n0": 0, "n1": 1, "n2": 0}
        """
        self._mapping = mapping

    def partition(self, nodes: List[QNode], num_ranks: int) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for node in nodes:
            if node.name in self._mapping:
                result[node.name] = self._mapping[node.name]
            else:
                result[node.name] = 0
        return result


class RoundRobinPartitioner(Partitioner):
    """
    Partition QNodes in a round-robin fashion across ranks.
    """

    def partition(self, nodes: List[QNode], num_ranks: int) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for i, node in enumerate(nodes):
            result[node.name] = i % num_ranks
        return result