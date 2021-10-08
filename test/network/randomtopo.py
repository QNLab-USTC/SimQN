from qns.network import QuantumNetwork
from qns.network.topology import RandomTopology

topo = RandomTopology(nodes_number=5, lines_number=10)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)