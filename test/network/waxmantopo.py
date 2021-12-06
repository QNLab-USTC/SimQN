from qns.network.network import QuantumNetwork
from qns.network.topology.waxmantopo import WaxmanTopology

topo = WaxmanTopology(nodes_number=10, size=1000, alpha=0.5, beta=0.5)
net = QuantumNetwork(topo)

print(net.nodes, net.qchannels)
