from qns.network.network import QuantumNetwork
from qns.network.topology.linetopo import LineTopology

topo = LineTopology(nodes_number=5)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)
