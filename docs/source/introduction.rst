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

Why use SimQN
---------------------------------------

Development Status
---------------------------------------