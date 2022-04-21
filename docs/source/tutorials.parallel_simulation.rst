Parallel Simulation: to run multiple simulations and leverage multiple CPUs
================================================================================

To provide a better performance in simulation, SimQN provides a method to create multiple processes and make full use of multiple CPUs.
To do so, users needs to create a sub-class of ``MPSimulations`` and overwrite ``run`` method to tell SimQN how to perform a single experiment.

The input parameter of ``run`` method, is a directory that contains all input variables, e.g., ``{"nodes_number": 5, "delay": 0.05, "memory_capacity": 10, "send_rate": 10}``, and the output is another directory containing all experiment results, e.g., ``{"throughput": 10, "fidelity": 0.88}``. Here is an example of how to build a ``MPSimulations``:

.. code-block:: python

    from qns.utils.multiprocess import MPSimulations
    from qns.network.route.dijkstra import DijkstraRouteAlgorithm
    from qns.network.topology.topo import ClassicTopology
    from qns.simulator.simulator import Simulator
    from qns.network import QuantumNetwork
    from qns.network.topology import LineTopology
    from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp
    
    
    class EPRDistributionSimulation(MPSimulations):
        def run(self, setting):

            # get input variables
            nodes_number = setting["nodes_number"]
            delay = setting["delay"]
            memory_capacity = setting["memory_capacity"]
            send_rate = setting["send_rate"]

            # do the experiments
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

            # form the result
            return {"count": src.apps[0].success_count}


Now, the ``EPRDistributionSimulation`` can be initiated by the following input parameters:

- ``settings``, a directory that contains all simulation variables. For example:

.. code-block:: python

    {
        "nodes_number": [5, 10, 15, 20],
        "delay": [0.05],
        "memory_capacity": [10, 20],
        "send_rate": [10, 20]
    }

It contains are four input variables, and the input parameter of each simulation will be the combination of all these four variables, e.g., ``{"nodes_number": 5, "delay": 0.05, "memory_capacity": 10, "send_rate": 10}``.

- ``iter_count``, the number of repeat experiments for each setting. If ``iter_count`` is 10, it means that the experiments will run for 10 times for each input variable combination.

- ``aggregate``, it is a boolean indicates whether to aggregate the results for the repeated simulations in a same input variable. If ``iter_count`` > 1, and ``aggregate`` is True, SimQN will aggregate the 10 results for each setting, and calculate the mean and std for every outputs.

- ``cores``, the number of processes. By default, SimQN will use all CPUs in this machine. For example, if ``cores`` = 1, SimQN will run in a single process mode.

- ``name``, the name of this simulation.

For example:

.. code-block:: python

    ss = EPRDistributionSimulation(settings={
        "nodes_number": [5, 10, 15, 20],
        "delay": [0.05],
        "memory_capacity": [10, 20],
        "send_rate": [10, 20]
    }, aggregate=True, iter_count=10, cores=4)

Finally, users can start the simulation and get the experiment results:

.. code-block:: python

    # start the simulation
    ss.start()

    # get the aggregated result (calculate the mean and std for every output variables).
    ss.get_data()

    # get the raw data
    ss.get_raw_data()

