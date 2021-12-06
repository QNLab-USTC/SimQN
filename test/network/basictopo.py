from qns.network.network import QuantumNetwork
from qns.network.topology.basictopo import BasicTopology

topo = BasicTopology(nodes_number=3)
net = QuantumNetwork(topo)

print(net.nodes)
