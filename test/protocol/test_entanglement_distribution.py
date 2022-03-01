import logging
from qns.network.route.dijkstra import DijkstraRouteAlgorithm
from qns.network.topology.topo import ClassicTopology
from qns.simulator.simulator import Simulator
from qns.network import QuantumNetwork
from qns.network.topology import LineTopology
import qns.utils.log as log
from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp


# constrains
init_fidelity = 0.99
nodes_number = 20
lines_number = 19
delay = 0.05
memory_capacity = 50
send_rate = 10
nodes_number = 10


def test_epr_distribution():
    s = Simulator(0, 10, accuracy=10000000)
    log.install(s)
    log.logger.setLevel(logging.DEBUG)
    topo = LineTopology(nodes_number=nodes_number,
                        qchannel_args={"delay": delay},
                        cchannel_args={"delay": delay},
                        memory_args={
                            "capacity": memory_capacity,
                            "store_error_model_args": {"a": 0.2}},
                        nodes_apps=[EntanglementDistributionApp(init_fidelity=init_fidelity)])

    net = QuantumNetwork(
        topo=topo, classic_topo=ClassicTopology.All, route=DijkstraRouteAlgorithm())
    net.build_route()

    src = net.get_node("n1")
    dst = net.get_node(f"n{nodes_number}")
    net.add_request(src=src, dest=dst, attr={"send_rate": send_rate})
    net.install(s)
    s.run()
