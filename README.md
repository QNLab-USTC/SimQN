# SimQN
[![Pytest](https://github.com/QNLab-USTC/SimQN/actions/workflows/pytest.yml/badge.svg?branch=main)](https://github.com/QNLab-USTC/SimQN/actions/workflows/pytest.yml)
![Flake8](https://github.com/QNLab-USTC/SimQN/actions/workflows/flake8.yml/badge.svg)
[![License](https://img.shields.io/badge/License-GPL_3.0-green?logo=github&logoColor=white)](LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/qns?style=flat&logo=pypi&label=PyPI)](https://pypi.org/project/qns/)&nbsp;
![GitHub Stars](https://img.shields.io/github/stars/QNLab-USTC/SimQN?style=flat&logo=github)&nbsp;
[![Citations](https://img.shields.io/badge/Citations-70-blue?style=flat&logo=googlescholar)](https://scholar.google.com/scholar?cites=17361842933401893020)&nbsp;
|[![Academic Usages](https://img.shields.io/badge/Academic_Usages-22-purple?style=flat)](https://github.com/QNLab-USTC/SimQN?tab=readme-ov-file#academic-paper-using-simqn-for-simulation)
[![Extensions](https://img.shields.io/badge/Extensions-7-orange?style=flat)](https://github.com/QNLab-USTC/SimQN?tab=readme-ov-file#platform-extension)&nbsp;

This Project is developed by [QNLab](https://qnlab-ustc.com/).

<img src="docs/assets/qnlab-logo.png" alt="QN-Lab | USTC" width="360" align="center" />


- [SimQN](#simqn)
  - [News](#news)
  - [Overview](#overview)
  - [Roadmap](#roadmap)
  - [Why choose SimQN?](#why-choose-simqn)
  - [Installation](#installation)
  - [First sight of SimQN](#first-sight-of-simqn)
  - [Get Help](#get-help)
  - [Release History](#release-history)
  - [Platform Extension](#platform-extension)
  - [How to contribute?](#how-to-contribute)
  - [License and Authors](#license-and-authors)
  - [Citation](#citation)
  - [Academic Paper using SimQN for Simulation](#academic-paper-using-simqn-for-simulation)

<h2 id="news">📰 News</h2>

* 🚀 **Version Update:** SimQN v0.2.3 has been released in June 2026.

* 📚 **Academic Papers:** SimQN has been implemented as the simulation platform in **22 peer-reviewed academic papers** (70 citations in total on Google Scholar).

* 🧩 **Platform Extension:** **7 simulation platforms or system extensions** have been built on SimQN, with more in development.

For more details, please refer to [Release History](#release-history), [Platform Extension](#platform-extension), and [Academic Paper Using SimQN for Simulation](#academic-paper-using-simqn-for-simulation).

<h2 id="overview">🔭 Overview</h2>

**[Attention]** Most of existing&future studies in [QNLab](https://qnlab-ustc.com/) are evaluated on SimQN platform. If you would like to follow our work or seek an easy-to-use quantum network simulator, you cannot miss SimQN! Please check out the following publication for details. **([Link](https://ieeexplore.ieee.org/abstract/document/10024900/) and [PDF](https://infonetlijian.github.io/homepage/PDF_files/2023-%E3%80%90IEEE%20Network%E3%80%91-SimQN_a_Network-layer_Simulator_for_the_Quantum_Network_Investigation.pdf)).**  

Welcome to SimQN's documentation. SimQN is a discrete-event-based network simulation platform for quantum networks.
SimQN enables large-scale investigations, including QKD protocols, entanglement distribution protocols, routing algorithms, and resource allocation schemas in quantum networks. For example, users can use SimQN to design routing algorithms for better QKD performance. For more information, please refer to the [Documents](https://qnlab-ustc.github.io/SimQN/).

SimQN is a Python3 library for quantum networking simulation. It is designed to be general purpose. It means that SimQN can be used for both QKD networks, entanglement distribution networks, and other kinds of quantum networks' evaluation. The core idea is that SimQN makes no architecture assumption. Since there is currently no recognized network architecture in quantum network investigations, SimQN stays flexible in this aspect.

SimQN provides high performance for large-scale network simulation. SimQN uses [Cython](https://cython.org/) to compile critical code in C/C++ libraries to boost the evaluation. Also, along with the commonly used quantum state-based physical models, SimQN provides a higher-layer fidelity-based entanglement physical model to reduce the computation overhead and bring convenience for users in evaluation. Last but not least, SimQN provides several network auxiliary models for easily building network topologies, producing routing tables, and managing multiple session requests.

We have already reproduced several academic papers using SimQN, and the open-source code can be found at our group [website](https://github.com/QNLab-USTC).


<h2 id="roadmap">🗺️ Roadmap</h2>

![Roadmap](https://github.com/QNLab-USTC/QuantumNetworkWebsite/blob/main/static/images/simqn_roadmap.png)

- Currently, we are focusing on developing the 0.2.x version of SimQN, which will include:
  - Useful network utilities, such as more random topology generators, routing algorithms, and session request generators, real topology adaptors, and Multi-path routing algorithms.
  - Representative quantum network protocols, such as Q-CAST routing protocol, PS/PU routing protocol, REPS routing protocol for quantum information networks, and CASCADE error correction protocol for QKD networks.

- The following functions will be included in the future versions:
  - Practical quantum network entities, such as quantum repeaters, quantum switches, and quantum benchmarking devices.
  - Useful network utilities, such as random request traffic generators.
  - Support for Quantum network stack protocols, including KM protocols, routing protocols in QKD networks, and entanglement distribution protocols in quantum information networks.
  - Realization of easy-to-use GUI for SimQN.
  
<h2 id="why-choose-simqn">❓ Why choose SimQN?</h2>

SimQN is designed as a functional and easy-to-use simulator, like [NS3](https://www.nsnam.org/) in classic networks, it provides numerous functions for anyone who wants to simulate a QKD network or entanglement-based network. 

Compared with the existing quantum network simulators, the developers pay more attention to simulation in the network area. Currently, a network simulation can be complicated, as users may have to implement routing algorithms and multiply protocols in different layers to complete a simulation. SimQN aims to break down this problem by providing a modulized quantum node and reusable algorithms and protocols. As a result, users can focus on what they study and reuse other built-in modules. The developers believe this will significantly reduce the burden on our users. As for the physics area, SimQN can also simulate quantum noise, fidelity, and more. Thus, if you focus on the research of the quantum network area, SimQN can be a competitive choice.  

**The main advantages of SimQN can be summarized as follows.**

- Easy-to-use with Python
- High-efficiency simulator core
- Customizable qubit model
- Built-in quantum internet protocol stack
- Mainstream quantum applications support, e.g., QKD, quantum networking, and distributed quantum computing (incoming)
- Periodical updates for academia-related functions and state-of-the-art solutions in the community  (you are welcome to highlight your work and contribute your code on SimQN)
- ...


<h2 id="installation">⚙️ Installation</h2>

Install and update using `pip`:
```
pip3 install -U qns
```

<h2 id="first-sight-of-simqn">👀 First sight of SimQN</h2>

Here is an example of using SimQN.

``` Python

    from qns.simulator.simulator import Simulator
    from qns.network.topology import RandomTopology
    from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp
    from qns.network import QuantumNetwork
    from qns.network.route.dijkstra import DijkstraRouteAlgorithm
    from qns.network.topology.topo import ClassicTopology
    import qns.utils.log as log
    import logging

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

<h2 id="get-help">❓ Get Help</h2>

- This [documentation](https://qnlab-ustc.github.io/SimQN/) may answer most questions.
    - The [tutorial](https://qnlab-ustc.github.io/SimQN/tutorials.html) here presents how to use SimQN.
    - The [API manual](https://qnlab-ustc.github.io/SimQN/modules.html) shows more detailed information.
- Welcome to report bugs at [Github](https://github.com/QNLab-USTC/SimQN).

<h2 id="release-history">📋 Release History</h2>

- v0.2.3(Released 2026.06)
  - *New funcation!!!*
  - Simulator Core: StableEventPool with Heap-Based Event Scheduling.
  - Network Utilities: Dijkstra Routing with Binary Heap, ClassicChannel Extension for Reliable Packet Delivery and Ordering, Link-decoherence quantum channel with differentiated link fidelity.

- v0.2.2(Released 2026.01)
  - *New functions!!!*
  - Simulator Core: Hash Bucket-Based Event Scheduler.
  - Network Utilities: Add Real Topology Generator, including AboveNetTopology, AGISTopology and Creat Topology From GML File Download From [The Internet Topology Zoo](https://topology-zoo.org/dataset.html). Update the Dijkstra-based Routing Utility.

- v0.2.1(Released 2025.04)
  - *New functions!!!*
  - Network Utilities: Add Random Topology Generator, including ER model, BA model, and dual-BA model.
  - Applications: Add CASCADE Error Correction and Privacy Amplification Process for BB84 Protocol.

- v0.1.5(Released 2022.09)
  - *New functions!!!*
  - Simulator Core: Cython Optimization, Multi-process Support.
  - Quantum Entitise: Quantum Memory, Delay Model.
  - Tools: Monitor Tools.

- v0.1.4(Released 2022.03)
  - *New functions!!!*
  - Simulator Core: Priority Queue-Based Event Scheduler.
  - Physical Backends: Qubit Model, EPR Model, Quantum Gates.
  - Quantum Entitise: Quantum Node, Quantum Channel.
  - Network Utilities: Topology Generator, Routing Utility.
  - Applications: BB84 Protocol, Entanglement Swapping Protocol.
  - Tools: Rnd Tools.

<h2 id="platform-extension">🧩 Platform Extension</h2>

- Josipa et al. enabled SimQN to accept structured data from upstream via the HTTP protocol by utilizing FastAPI, thereby developing a [Docker environment for QKD network simulations](https://repozitorij.fpz.unizg.hr/object/fpz:3666). [2025]
- Majid K et al. integrated SimQN with the open-source OpenAirInterface (OAI) stack to deploy a 5G standalone network capable of supporting quantum operations, proposing the [quantum-inspired RAN (Q-RAN)](https://ieeexplore.ieee.org/abstract/document/11432359), a next-generation framework. [2025]
- Abane et al. developed [MQNS](https://ieeexplore.ieee.org/abstract/document/11334170) based on SimQN v0.1.5, leveraging the simulator core, entities, and tools to enable simulation under dynamic, heterogeneous configurations. [2025]
- [Fidelity-Guaranteed-Entanglement-Routing](https://github.com/infonetlijian/Fidelity-Guaranteed-Entanglement-Routing) ⭐11: Complete simulation code for fidelity-guaranteed entanglement routing in quantum networks. [2025]
- [Load-Balancing-Quantum-Routing-SimQN](https://github.com/MLCL-SYSU/Load-balancing-quantum-routing-SimQN): Implementation of a load balancing quantum routing algorithm using SimQN. [2025]
- [QKDsim](https://github.com/zp2333/QKDsim) ⭐2: A QKD network simulation system implemented based on SimQN. [2025]
- [Q-cast](https://github.com/tanjiesheng/Q-cast): A quantum communication simulation platform built on SimQN, supporting multicast entanglement distribution and routing. [2025]

<h2 id="how-to-contribute">🤝 How to contribute?</h2>
Welcome to contribute through GitHub Issue or Pull Requests. Please refer to the [develop guide](https://qnlab-ustc.github.io/SimQN/develop.html). If you have any questions, you are welcome to contact the developers via e-mail.

<h2 id="license-and-authors">🪪 License and Authors</h2>

SimQN is an open-source project under [GPLv3](/LICENSE) license. The authors of the paper include:
* Lutong Chen (ertuil), School of Cyber Science and Technology, University of Science and Technology of China, China. elliot.98@outlook.com
* Jian Li(infonetlijian), School of Cyber Science and Technology, University of Science and Technology of China, China. lijian9@ustc.edu.cn
* Kaiping Xue (kaipingxue), School of Cyber Science and Technology, University of Science and Technology of China, China. xue.kaiping@gmail.com & kpxue@ustc.edu.cn
* Nenghai Yu, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Ruidong Li, Institute of Science and Engineering, Kanazawa University, Japan.
* Qibin Sun, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Jun Lu, School of Cyber Science and Technology, University of Science and Technology of China, China.

Other contributors include:
* Zirui Xiao, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Yuqi Yang, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Bing Yang, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Xumin Gao, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Yuxin Chen, School of Information Science and Technology, University of Science and Technology of China, China.
* ShaoChuang Heng, School of Cyber Science and Technology, University of Science and Technology of China, China.
* Jianfeng Niu, School of Cyber Science and Technology, University of Science and Technology of China, China.

<h2 id="citation">📝 Citation</h2>

Please cite this publication if you use SimQN in your research.

```Bibtex
@article{chen2023simqn,
  title={SimQN: A network-layer simulator for the quantum network investigation},
  author={Chen, Lutong and Xue, Kaiping and Li, Jian and Yu, Nenghai and Li, Ruidong and Sun, Qibin and Lu, Jun},
  journal={IEEE Network},
  volume={37},
  number={5},
  pages={182--189},
  year={2023},
  publisher={IEEE},
  doi={10.1109/MNET.130.2200481}
}
```

<h2 id="academic-paper-using-simqn-for-simulation">📚 Academic Paper using SimQN for Simulation</h2>

1. Wang Z, Gong T, Ji B, et al. REAP-Q: Resource-Aware Efficient Routing and Adaptive Purification for High-Fidelity Entanglement Distribution[C]//2026 International Wireless Communications and Mobile Computing (IWCMC). IEEE, 2026: 699-704.
2. Abane A, Shi J, Mai V S, et al. Multiverse: A Simulator for Evaluating Entanglement Routing in Quantum Networks[J]. IEEE Internet Computing, 2026.
3. Ikken N, Kumar P, Slaoui A, et al. Optimizing multi-hop quantum communication using bidirectional quantum teleportation protocol[J]. arXiv preprint arXiv:2504.07320, 2025.
4. Kumar P, Kar B. ZBR: Zone-based routing in quantum networks with efficient entanglement distribution[J]. Journal of Network and Computer Applications, 2025, 238: 104156.
5. Kumar P, Kar B, Shen S H. Trace-distance based end-to-end entanglement fidelity with information preservation in quantum networks[J]. Journal of Network and Computer Applications, 2025: 104366.
6. Chen Y, Li J, Li Z, et al. An Asynchronous Key Relay Protocol Design for Large-Scale Quantum Key Distribution Networks[J]. IEEE Transactions on Networking, 2025.
7. Zheng P, Li J, Li Z, et al. An efficient and robust resource allocation method for quantum key distribution networks[J]. IEEE Transactions on Network and Service Management, 2025.
8. Yang Y, Li Z, Li J, et al. An On-demand Routing Scheme with QoS Provisioning for QKD Networks[C]//2025 International Conference on Quantum Communications, Networking, and Computing (QCNC). IEEE, 2025: 224-231.
9. Tan J, Li Z, Li J, et al. Distributed Entanglement Routing Scheme With Fidelity Guarantee in Quantum Networks[J]. IEEE Transactions on Network Science and Engineering, 2025, 13: 3320-3334.
10. Li J, Zheng P, Li Z, et al. Integration of quantum key distribution networks and classical networks: An evolution perspective[J]. IEEE Network, 2025.
11. Liu X, Li R. Quantum Network Routing Design with Dynamic Requests Scheduling in Multi-User Environments[C]//2025 International Wireless Communications and Mobile Computing (IWCMC). IEEE, 2025: 1434-1439.
12. Yang B, Li Z, Xue K, et al. SwappingBoost: Optimizing entanglement routing by mitigating bottlenecks in quantum networks[C]//2025 International Wireless Communications and Mobile Computing (IWCMC). IEEE, 2025: 1-6.
13. Wu J, Chen L, Zhang J, et al. A distributed routing protocol based on key reservation in quantum key distribution networks[C]//ICC 2024-IEEE International Conference on Communications. IEEE, 2024: 509-514.
14. Liu C, Che X, Xie J, et al. A multi-path QKD algorithm with multiple segments[J]. Journal of Cyber Security and Mobility, 2024, 13(2): 193-214.
15. Bayleyegn A A, Tunc H S D, Bassoli R, et al. Impact of Network Latency on Entanglement Distribution in Quantum Repeaters Network[C]//European Wireless 2024; 29th European Wireless Conference. VDE, 2024: 134-139.
16. Li J, Wang Z, Xue K, et al. DRM-ETP: A Dynamic Rate Matching-Based Entanglement Transport Protocol in Quantum Networks[J]. IEEE Transactions on Networking, 2024, 33(2): 835-848.
17. Li Z, Li J, Xue K, et al. NarrowGap: Reducing bottlenecks for end-to-end entanglement distribution in quantum networks[J]. IEEE Transactions on Networking, 2024, 33(1): 162-177.
18. Chen L, Xue K, Li J, et al. REDP: Reliable entanglement distribution protocol design for large-scale quantum networks[J]. IEEE Journal on Selected Areas in Communications, 2024, 42(7): 1723-1737.
19. Li P, Li W. Traffic-Aware Routing Algorithm in Quantum Network[C]//2024 9th International Conference on Computer and Communication Systems (ICCCS). IEEE, 2024: 706-711.
20. Xiao Z, Li J, Xue K, et al. Purification scheduling control for throughput maximization in quantum networks[J]. Communications Physics, 2024, 7(1): 307.
21. Xiao Z, Li J, Xue K, et al. A connectionless entanglement distribution protocol design in quantum networks[J]. IEEE Network, 2023, 38(1): 131-139.
22. Chen L, Xue K, Li J, et al. Q-DDCA: Decentralized dynamic congestion avoid routing in large-scale quantum networks[J]. IEEE/ACM Transactions on Networking, 2023, 32(1): 368-381.


