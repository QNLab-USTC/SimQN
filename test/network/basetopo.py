from qns.network import QuantumNetwork
from qns.network.topology import BasicTopology

topo = BasicTopology(nodes_number=3)
net = QuantumNetwork(topo)

print(net.nodes)