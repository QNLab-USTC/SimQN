from qns.network.network import QuantumNetwork
from qns.network.topology.randomtopo import RandomTopology

topo = RandomTopology(nodes_number=5, lines_number=10)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)
