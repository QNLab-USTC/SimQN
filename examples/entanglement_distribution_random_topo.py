import logging

from qns.network.route.dijkstra import DijkstraRouteAlgorithm
from qns.network.topology.topo import ClassicTopology
from qns.simulator.simulator import Simulator
from qns.network import QuantumNetwork
from qns.network.topology import RandomTopology
import qns.utils.log as log
from qns.utils.random import set_seed
from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp

# constrains
init_fidelity = 0.99
nodes_number = 150
lines_number = 450
qchannel_delay = 0.05
cchannel_delay = 0.05
memory_capacity = 50
send_rate = 10
requests_number = 10

log.logger.setLevel(logging.INFO)

for requests_number in [10, 20, 30, 40]:
    for nodes_number in range(20, 201, 10):
        lines_number = 3 * nodes_number
        # set a fixed random seed
        set_seed(100)
        s = Simulator(0, 10, accuracy=1000000)
        log.install(s)

        topo = RandomTopology(nodes_number=nodes_number,
                              lines_number=lines_number,
                              qchannel_args={"delay": qchannel_delay},
                              cchannel_args={"delay": cchannel_delay},
                              memory_args=[{"capacity": memory_capacity}],
                              nodes_apps=[EntanglementDistributionApp(init_fidelity=init_fidelity)])

        net = QuantumNetwork(
            topo=topo, classic_topo=ClassicTopology.All, route=DijkstraRouteAlgorithm())

        net.build_route()
        try:
            net.random_requests(requests_number, attr={"send_rate": send_rate})
        except Exception:
            continue
        net.install(s)

        s.run()
        results = []
        for req in net.requests:
            src = req.src
            results.append(src.apps[0].success_count)
        fair = sum(results)**2 / (len(results) * sum([r**2 for r in results]))
        log.monitor(requests_number, nodes_number, s.time_spend, sep=" ")
