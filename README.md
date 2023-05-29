# SimQN

![Pytest](https://github.com/ertuil/SimQN/actions/workflows/pytest.yml/badge.svg) 
![Flake8](https://github.com/ertuil/SimQN/actions/workflows/flake8.yml/badge.svg) 

Welcome to SimQN's documentation. SimQN is a discrete-event based network simulation platform for quantum networks.
SimQN enables large-scale investigations, including QKD protocols, entanglement distributions protocols, and routing algorithms, resource allocation schemas in quantum networks. For example, users can use SimQN to design routing algorithms for better QKD performance. For more information, please refer to the [Documents](https://ertuil.github.io/SimQN/).

SimQN is a Python3 library for quantum networking simulation. It is designed to be general propose. It means that SimQN can be used for both QKD network, entanglement distribution network and other kinds of quantum networks' evaluation. The core idea is that SimQN makes no architecture assumption. Since there is currently no recognized network architecture in quantum networks investigations, SimQN stays flexible in this aspect.

SimQN provides high performance for large-scale network simulation. SimQN use [Cython](https://cython.org/) to compile critical codes in C/C++ libraries to boost the evaluation. Also, along with the common used quantum state based physical models, SimQN provides a higher-layer fidelity based entanglement physical model to reduce the computation overhead and brings convenience for users in evaluation. Last but not least, SimQN provides several network auxiliary models for easily building network topologies, producing routing tables and managing multiple session requests.

## Get Help

- This [documentation](https://ertuil.github.io/SimQN/) may answer most questions.
    - The [tutorial](https://ertuil.github.io/SimQN/tutorials.html) here presents how to use SimQN.
    - The [API manual](https://ertuil.github.io/SimQN/modules.html) shows more detailed information.
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
```
# FAQ
## Why choose SimQN?
SimQN is designed as a functional and easy-to-use simulator, like [NS3](https://www.nsnam.org/) in classic networks, it provides numerous functions for anyone who wants to simulate a QKD network or entanglement-based network. 

Compared with the existing quantum network simulators, the developers pay more attention to simulation in the network area. Currently, a network simulation can be complicated, as users may have to implement routing algorithms and multiply protocols in different layers to complete a simulation. SimQN aims to break down this problem by providing a modulized quantum node and reusable algorithms and protocols. As a result, users can focus on what they study and reuse other built-in modules. The developers believe this will significantly reduce the burden on our users. As for the physics area, SimQN can also simulate quantum noise, fidelity, and more. Thus, if you focus on the research of the quantum network area, SimQN can be a competitive choice. 

## How to contribute?
Welcome to contribute through Github Issue or Pull Requests. Please refer to the [develop guide](https://ertuil.github.io/SimQN/develop.html). If you have any questions, you are welcome to contact the developers via e-mail.

## License and Authors

SimQN is an open-source project under [GPLv3](/LICENSE) license. The authors of the paper includes:
* Lutong Chen (ertuil), School of Cyber Science and Technology, University of Science and Technology of China, China. elliot.98@outlook.com
* Jian Li(infonetlijian), School of Cyber Science and Technology, University of Science and Technology of China, China.
* Kaiping Xue (kaipingxue), School of Cyber Science and Technology, University of Science and Technology of China, China. xue.kaiping@gmail.com
* Nenghai Yu, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Ruidong Li, Institute of Science and Engineering, Kanazawa University, Japan.
* Qibin Sun, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Jun Lu, School of Cyber Science and Technology, University of Science and Technology of China, China.

Other contributors includes:
* Zirui Xiao, School of Cyber Science and Technology, University of Science and Technology of China, China.
