Introduction
=======================================

Overview
---------------------------------------

Welcome to SimQN's documentation. SimQN is a discrete-event based network simulation platform for quantum networks.
SimQN enables large-scale investigations, including QKD protocols, entanglement distributions protocols, and routing algorithms, resource allocation schemas in quantum networks. For example, users can use SimQN to design routing algorithms for better QKD performance.

SimQN is a Python3 library for quantum networking simulation. It is designed to be general propose. It means that SimQN can be used for both QKD network, entanglement distribution network and other kinds of quantum networks' evaluation. The core idea is that SimQN makes no architecture assumption. Since there is currently no recognized network architecture in quantum networks investigations, SimQN stays flexible in this aspect.

SimQN provides high performance for large-scale network simulation. Besides the common used quantum state based physical models, SimQN provides a higher-layer fidelity based entanglement physical model to reduce the computation overhead and brings convenience for users in evaluation.

Bootstrap is anther core feature when designing SimQN. SimQN provides several network auxiliary models for easily building network topologies, producing routing tables and managing multiple session requests.

Module Design
---------------------------------------

The architecture of SimQN has several modules, includes:

- `qns.simulator`, the discrete-event driven simulator.
- `qns.models`, the physical model for qubits or entanglements.
- `qns.entity`, basic entities in the quantum networks, including nodes, memories, channels.
- `qns.network`, network auxiliary tools, such as topology generator, routing algorithms.
- `qns.utils`, logging, random generator and other utilities.

.. image:: _imgs/modules.png
   :align: center
   :alt: Moduels
   :width: 400px

Develop Status
---------------------------------------

Currently, SimQN is in its initial version that we believe it can help the quantum network researches. We still contribute to enable more features and functionalities, that means APIs may still change. Besides, not all functions are well tested. As a result, SimQN can be used as early validation in this period.

We encourage the community to report bugs, bring suggestions to us so that we can make SimQN as realistic as possible. The :doc:`develop` contains more information about this topic.