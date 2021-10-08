from qns.network import QuantumNetwork
from qns.network.topology import GridTopology

topo = GridTopology(nodes_number=9)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)