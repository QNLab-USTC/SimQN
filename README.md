# SimQN

Welcome to SimQN's documentation. SimQN is a discrete-event based network simulation platform for quantum networks.
SimQN enables large-scale investigations, including QKD protocols, entanglement distributions protocols, and routing algorithms, resource allocation schemas in quantum networks. For example, users can use SimQN to design routing algorithms for better QKD performance. For more information, please refer to the [Documents](https://ertuil.github.io/SimQN/).

SimQN is a Python3 library for quantum networking simulation. It is designed to be general propose. It means that SimQN can be used for both QKD network, entanglement distribution network and other kinds of quantum networks' evaluation. The core idea is that SimQN makes no architecture assumption. Since there is currently no recognized network architecture in quantum networks investigations, SimQN stays flexible in this aspect.

SimQN provides high performance for large-scale network simulation. Besides the common used quantum state based physical models, SimQN provides a higher-layer fidelity based entanglement physical model to reduce the computation overhead and brings convenience for users in evaluation. Bootstrap is anther core feature when designing SimQN. SimQN provides several network auxiliary models for easily building network topologies, producing routing tables and managing multiple session requests.

## Get Help

- This [documentation](https://ertuil.github.io/SimQN/) many answer most questions.
- Welcome to report bugs at [Github](https://github.com/ertuil/SimQN).

## Installation

Install and update using `pip`:
```
pip3 install -U qns
```

# First sight of SimQN

Here is an example of using SimQN.

``` Python

    from qns.simulator.simulator import Simulator
    from qns.network.topology import RandomTopology
    from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp
    from qns.network import QuantumNetwork
    from qns.network.route.dijkstra import DijkstraRouteAlgorithm
    from qns.network.topology.topo import ClassicTopology
    import qns.utils.log as log

    init_fidelity = 0.99 # the initial entanglement's fidelity 
    nodes_number = 150 # the number of nodes
    lines_number = 450 # the number of quantum channels
    qchannel_delay = 0.05 # the delay of quantum channels
    cchannel_delay = 0.05 # the delay of classic channels
    memory_capacity = 50 # the size of quantum memories
    send_rate = 10 # the send rate
    requests_number = 10 # the number of sessions (SD-pairs)

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
    net = QuantumNetwork( topo=topo, classic_topo=ClassicTopology.All, route=DijkstraRouteAlgorithm())

    # build the routing table
    net.build_route()

    # randomly select multiple sessions (SD-paris)
    net.random_requests(requests_number, attr={"send_rate": send_rate})

    # all entities in the network will install the simulator and do initiate works.
    net.install(s)

    # run simulation
    s.run()

    # count the number of successful entanglement distribution for each session
    results = [src.apps[0].success_count for req in net.requests]

    # log the results
    log.monitor(requests_number, nodes_number, results, s.time_spend, sep=" ")
```

# Contributing
Welcome to contribute through Github Issue or Pull Requests. Please refer to the [develop guide](https://ertuil.github.io/SimQN/develop.html).
