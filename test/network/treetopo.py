from qns.network.network import QuantumNetwork
from qns.network.topology.treetopo import TreeTopology

topo = TreeTopology(nodes_number=15, children_number=3)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)
