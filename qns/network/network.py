from typing import Optional
from qns.entity import QNode, QuantumChannel
from qns.network.topology import Topology, BasicTopology

class QuantumNetwork(object):
    """
    QuantumNetwork includes several quantum nodes, channels and a special topology
    """

    def __init__(self, topo: Optional[Topology]):
        if topo is None:
            self.nodes = []
            self.qchannels = []
        else:
            self.nodes, self.qchannels = topo.build()