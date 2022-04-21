Monitor: for better collecting network status
==================================================

``Monitor`` is a virtual entity to collect network status for better analysis. It can collect network status before the simulation starts, after the simulation finishes, periodically, or when be triggered by a serial of events. It can be initiated by the following input parameters:

- name, the name of this monitor
- network, a optional input parameter, a ``QuantumNetwork`` object.

.. code-block:: python

    from qns.entity.Monitor.monitor import Monitor

    monitor = Monitor(name="monitor_1", network = None)


Users should instruct monitors how to collect the data by providing a calculate function. They can use the method ``add_attribution`` to add a new watching data. The first parameter is the attribution's name (the column's name in pandas), and the second parameter is the calculate function ``calculate_func``. This function will be called whenever the monitor is triggered. The input of ``calculate_func`` is a tuple (``Simulator``, ``QuantumNetwork``, ``Event``), so that ``calculate_func`` can get what they need from those input. The output is the calculated collecting data. Here are some examples. 

.. code-block:: python

    def watch_send_count(simulator, network, event):
        return sp.count

    def watch_recv_count(simulator, network, event):
        return rp.count

    monitor.add_attribution(name="send_count", calculate_func=watch_send_count)
    monitor.add_attribution(name="recv_count", calculate_func=watch_recv_count)
    monitor.add_attribution(name="event_name", calculate_func=lambda s, n, e: e.__class__)

Finally, users should tell the monitor when to collect data. SimQN provides the following hooks:

.. code-block:: python

    # before the simulation starts
    m.at_start()

    # after it finishes
    m.at_finish()

    # at a fixed period time
    m.at_period(period_time=1)

    # watch every ``RecvQubitPacket`` Event
    m.at_event(RecvQubitPacket)

Before the simulation start, the monitor should be installed to the simulator by ``install`` method. After the simulation finishes, users can get the collected data using ``get_data`` function. The data will be formed in a ``pandas.DataFrame`` object.

.. code-block:: python

    m.install(s)
    s.run()
    data = m.get_data()