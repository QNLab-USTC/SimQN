from qns.simulator.simulator import Simulator
from qns.network.topology import RandomTopology
from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp
from qns.network import QuantumNetwork
from qns.network.route.dijkstra import DijkstraRouteAlgorithm
from qns.network.topology.topo import ClassicTopology
import qns.utils.log as log
import logging


def test_example_readme():
    init_fidelity = 0.99   # the initial entanglement's fidelity
    nodes_number = 150     # the number of nodes
    lines_number = 450     # the number of quantum channels
    qchannel_delay = 0.05  # the delay of quantum channels
    cchannel_delay = 0.05  # the delay of classic channels
    memory_capacity = 50   # the size of quantum memories
    send_rate = 10         # the send rate
    requests_number = 10   # the number of sessions (SD-pairs)

    # generate the simulator
    s = Simulator(0, 10, accuracy=1000000)

    # set the log's level
    log.logger.setLevel(logging.INFO)
    log.install(s)

    # generate a random topology using the parameters above
    # each node will install EntanglementDistributionApp for hop-by-hop entanglement distribution
    topo = RandomTopology(nodes_number=nodes_number,
                          lines_number=lines_number,
                          qchannel_args={"delay": qchannel_delay},
                          cchannel_args={"delay": cchannel_delay},
                          memory_args=[{"capacity": memory_capacity}],
                          nodes_apps=[EntanglementDistributionApp(init_fidelity=init_fidelity)])

    # build the network, with Dijkstra's routing algorithm
    net = QuantumNetwork(topo=topo, classic_topo=ClassicTopology.All, route=DijkstraRouteAlgorithm())

    # build the routing table
    net.build_route()

    # randomly select multiple sessions (SD-pars)
    net.random_requests(requests_number, attr={"send_rate": send_rate})

    # all entities in the network will install the simulator and do initiate works.
    net.install(s)

    # run simulation
    s.run()


if __name__ == "__main__":
    test_example_readme()
