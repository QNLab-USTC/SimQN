from qns.network import QuantumNetwork
from qns.network.topology import RandomTopology, LineTopology

# topo = RandomTopology(nodes_number=5, lines_number=4)
topo = RandomTopology(nodes_number=20, lines_number= 30)
net = QuantumNetwork(topo)

net.build_route()
print(net.nodes)
for l in net.qchannels:
    print(l, l.node_list)

n1 = net.get_node("n1")
n4 = net.get_node("n4")
print(net.route.route_table)
print(net.query_route(n1, n4))

net.add_request(n1, n4)
print(net.requests)

net.random_requests(5, allow_overlay=False)
print(net.requests)

net.random_requests(5, allow_overlay=True)
print(net.requests)