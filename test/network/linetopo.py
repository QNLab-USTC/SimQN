from qns.network import QuantumNetwork
from qns.network.topology import LineTopology

topo = LineTopology(nodes_number=5)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)