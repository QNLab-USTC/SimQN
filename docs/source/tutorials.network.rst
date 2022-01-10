Construct large-scale networks
===============================

SimQN provides a ``QuantumNetwork`` to help build large-scale topologies, generate routing tables and manage multiple sessions. It can be initiate with the follow parameters:

- ``topo``: the optional quantum network topology generator. It can be used to produce several quantum nodes, channels and form a special topology.
- ``classic_topo``: an ``Enum`` class indicate the classic topology. 
- ``route``: the optional routing algorithm implement.
- ``name``: the networks' name

The ``QuantumNetwork`` provides the following functions:

.. toctree::
   :maxdepth: 4

   tutorials.network.topology
   tutorials.network.route
   tutorials.network.request
