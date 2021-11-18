from qns.entity import node
from qns.entity.cchannel.cchannel import ClassicChannel
from qns.entity.memory.memory import QuantumMemory
from qns.entity.node.app import Application
from typing import Dict, List, Optional, Tuple
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode

from enum import Enum, auto
import itertools

class ClassicTopology(Enum):
    Empty = 1
    All = 2
    Follow = 3

class Topology(object):
    """
    Topology is a factory for QuantumNetwork
    """

    def __init__(self, nodes_number: int, nodes_apps: List[Application] = [], qchannel_args: Dict = {}, cchannel_args: Dict = {}, memory_args: Optional[List[Dict]] = {}):
        """
        Args:
            nodes_number: the number of Qnodes
            nodes_apps: apps will be installed to all nodes
            qchannel_args: default quantum channel arguments
            cchannel_args: default channel channel arguments
            memory_args: default quantum memory arguments
        """
        self.nodes_number = nodes_number
        self.nodes_apps = nodes_apps
        self.qchannel_args = qchannel_args
        self.memory_args = memory_args
        self.cchannel_args = cchannel_args

    def build(self) -> Tuple[List[QNode], List[QuantumChannel]]:
        """
        build the special topology

        Returns:
            the list of QNodes and the list of QuantumChannel
        """
        pass

    def _add_apps(self, nl: List[QNode]):
        """
        add apps for all nodes in `nl`

        Args:
            nl (List[QNode]): a list of quantum nodes
        """
        for n in nl:
            for p in self.nodes_apps:
                n.add_apps(p)

    def _add_memories(self, nl: List[QNode]):
        """
        Add quantum memories to all nodes in `nl`

        Args:
            nl (List[QNode]): a list of quantum nodes
        """
        if self.memory_args is None:
            return
        for idx, n in enumerate(nl):
            m = QuantumMemory(name=f"m{idx}", node = n, **self.memory_args)
            n.add_memory(m)

    def add_cchannels(self, classic_topo: ClassicTopology = ClassicTopology.Empty , nl: List[QNode] = [], ll: Optional[List[QuantumChannel]] = None):
        """
        build classic network topology

        Args:
            classic_topo (ClassicTopology): Classic topology, ClassicTopology.Empty -> no connection, ClassicTopology.All -> every nodes are connected directly, ClassicTopology.Follow -> follow the quantum topology
            nl (List[QNode]): a list of quantum nodes
            ll (List[QuantumChannel]): a list of quantum channels
        """
        cchannel_list = []
        if classic_topo == ClassicTopology.All:
            topo = list(itertools.combinations(nl, 2))
            for idx, (src, dst) in enumerate(topo):
                cchannel = ClassicChannel(name = f"c{idx+1}", **self.cchannel_args)
                src.add_cchannel(cchannel = cchannel)
                dst.add_cchannel(cchannel = cchannel)
                cchannel_list.append(cchannel)
        if classic_topo == ClassicTopology.Follow:
            if ll is None:
                return cchannel_list
            for idx, qchannel in enumerate(ll):
                node_list = qchannel.node_list
                cchannel = ClassicChannel(name = f"c-{qchannel.name}", **self.cchannel_args)
                for n in node_list:
                    n.add_cchannel(cchannel = cchannel)
                cchannel_list.append(cchannel)
        return cchannel_list