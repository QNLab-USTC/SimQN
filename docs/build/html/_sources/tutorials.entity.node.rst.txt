Quantum node: the end-point users, routers and repeaters
===========================================================

Quantum nodes are the parties in the quantum network. They can be end-point users, quantum routers, switches and repeaters. Quantum nodes may equip devices for quantum measurement and operations. They can also have quantum memories and share quantum channel and classic channels.

Quantum node can be generated, and they can also equip memories and channels:

.. code-block:: python

    from qns.entity.node.node import QNode
    from qns.entity.memory.memory import QuantumMemory
    from qns.entity.qchannel.qchannel import QuantumChannel
    from qns.entity.cchannel.cchannel import ClassicChannel

    n1 = QNode("n1") # a quantum node named "n1"

    # add quantum memory
    m = QuantumMemory("m1")
    n1.add_memory(m)

    # add classic channel
    cl1 = ClassicChannel(name="cl1", bandwidth=10, delay=0.2, drop_rate=0.1, max_buffer_size=30)
    n1.add_cchannel(cl1)

    # add quantum channel
    ql1 = QuantumChannel(name="ql1", bandwidth=3, delay=0.2, drop_rate=0.1, max_buffer_size=5)
    n1.add_qchannel(ql1)

It is also possible to get the channel by the destination by ``get_cchannel`` or ``get_channel``:

.. code-block:: python

    n1 = QNode("n1")
    n2 = QNode("n2")

    # add a quantum channel
    ql1 = QuantumChannel(name="ql1", bandwidth=3, delay=0.2)
    n1.add_qchannel(ql1)
    n2.add_qchannel(ql1)

    # get the quantum channel by destination
    assert(ql1 == n1.get_qchannel(n2))

Applications
----------------

Quantum nodes may behavior differently. For example, some nodes may be the sender and other may be the receiver. Nodes in the quantum networks may be the routers or switches. Thus, quantum nodes can install different ``Applications``. Applications are the programmes running on the quantum nodes.

It is possible to install and get applications:

.. code-block:: python

    from qns.network.protocol.entanglement_distribution import EntanglementDistributionApp
    from qns.entity.node.node import QNode

    app = EntanglementDistributionApp() # the application
    n1 = QNode("n1")
    
    # add an application
    n1.add_apps(app)

    # get applications by the class
    assert(app == n1.get_apps(EntanglementDistributionApp)[0])

    # install application when generate the quantum node
    n2 = QNode("n2", apps = [EntanglementDistributionApp()])

The application can get the related node and simulator:

.. code-block:: python

    node = app.get_node()
    simulator = app.get_simulator()

The application needs to implements the following two methods:

- ``install``: initiate the application and inject initial events 
- ``handle``: handle the incoming events

One example is:

.. code-block:: python

    from qns.entity.node.app import Application

    class PrintApp(Application):
        def __init__(self):
            super().__init__()
    
        def install(self, node, simulator: Simulator):
            # initiate the application
            super().install(node, simulator)
            print("init")
    
        def handle(self, node, event: Event):
            # called when the event happens
            print(f"event {event} happens")

Other examples can be found at ``qns.network.protocols``.

Initiate and event handling process
---------------------------------------

Both nodes and applications has ``install`` and ``handle`` methods. The relation is:

1. The nodes' ``install`` method will call every memories, channels and applications' ``install`` method to initiate every sub-entities and applications.
2. The application's ``install`` method should be implemented by users and do the 'dirty work' to actually initiate the node's state.
3. When an related event happends, the node' ``handle`` method will call all its applications' ``handle`` method to handle the event.
4. The application's ``handle`` method should be implemented by users to actually handle the events