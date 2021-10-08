from qns.network import QuantumNetwork
from qns.network.topology import TreeTopology

topo = TreeTopology(nodes_number=15, children_number = 3)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)