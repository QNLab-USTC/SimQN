from qns.utils.multiprocess import MPSimulations
from qns.network.route.dijkstra import DijkstraRouteAlgorithm
from qns.network.topology.topo import ClassicTopology
from qns.simulator.simulator import Simulator
from qns.network import QuantumNetwork
from qns.network.topology import LineTopology
from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp


class EPRDistributionSimulation(MPSimulations):
    def run(self, setting):
        nodes_number = setting["nodes_number"]
        delay = setting["delay"]
        memory_capacity = setting["memory_capacity"]
        send_rate = setting["send_rate"]
        s = Simulator(0, 10, accuracy=10000000)
        topo = LineTopology(nodes_number=nodes_number,
                            qchannel_args={"delay": delay, "drop_rate": 0.3},
                            cchannel_args={"delay": delay},
                            memory_args={
                                "capacity": memory_capacity,
                                "store_error_model_args": {"a": 0.2}},
                            nodes_apps=[EntanglementDistributionApp(init_fidelity=0.99)])

        net = QuantumNetwork(
            topo=topo, classic_topo=ClassicTopology.All, route=DijkstraRouteAlgorithm())
        net.build_route()

        src = net.get_node("n1")
        dst = net.get_node(f"n{nodes_number}")
        net.add_request(src=src, dest=dst, attr={"send_rate": send_rate})
        net.install(s)
        s.run()
        return {"count": src.apps[0].success_count}


if __name__ == "__main__":
    ss = EPRDistributionSimulation(settings={
        "nodes_number": [5, 10, 15, 20],
        "delay": [0.05],
        "memory_capacity": [10, 20],
        "send_rate": [10, 20]
    }, aggregate=True, iter_count=10, cores=1)
    ss.start()
    print(ss.get_data())
