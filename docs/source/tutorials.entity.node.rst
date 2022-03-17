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

It is possible to install and get the existing applications:

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

How to build an application
--------------------------------

There are two kinds of behaviors for an application. On one hand, it may generate some initial events positively. For example, the sender applications may generate the first send packet event begins. On the other hand, the application may wait and listen to a certain event and handling the event.

For the positive mode, users can use ``install`` function to generate several events at the beginning of the simulation. For the passive mode, users can implement their own handler methods to handle events. The handler methods must have the following input parameters:
- self, the application itself
- node, the related quantum node
- event, the calling event,
and can have an option return variable ``pass``. If ``pass`` is ``True``, the following applications on this node will not handle this event any more. An example of the handler function is:

.. code-block:: python

    def RecvClassicPacketHandler(self, node: QNode, event: Event):
        packet = event.packet
        msg = packet.get()
        print(f"{node} recv packet: {msg} from {packet.src}->{packet.dest}")
        return True # bypass the following applications

Users can use ``add_handler`` to bind the handler to one or more events. ``add_handler`` have three input parameters. The first is the handler method. The second parameter``EventTypeList`` is a list of event types that will trigger this handler. If the list is empty, this handler will be called when all kinds of events. The third parameter ``ByList`` is a list of the event source. For example, it is possible to handle classic messages from node "n1" and "n2" but not "n3". If the list is empty, it means that no matter which entity generate this event, it will be handled by this handler function

.. code-block:: python

    from qns.entity.node.app import Application

    class PrintApp(Application):
        def __init__(self):
            super().__init__()
    
        def install(self, node, simulator: Simulator):
            # initiate the application
            super().install(node, simulator)
            print("initiate app")

            # RecvClassicPacketHandler should handle classic packets from node n2
            self.add_handler(RecvClassicPacketHandler, [RecvClassicPacket], [n1, n2])
            print("init")
    
        def RecvClassicPacketHandler(self, node: QNode, event: Event):
            packet = event.packet
            msg = packet.get()
            print(f"{node} recv packet: {msg} from {packet.src}->{packet.dest}")
            return True # bypass the following applications


Other examples of applications can be found at ``qns.network.protocols``.

Processing delay on quantum nodes
-------------------------------------

It is possible to add a processing delay on quantum nodes whenever they receive certain events. It is implemented in ``NodeProcessDelayApp``. Here is an example:

.. note::
    The ``NodeProcessDelayApp`` must be added to nodes before other applications so that it will handle all incoming events first.

.. code-block:: python

    from qns.entity.node.app import Application
    from qns.network.protocol.node_process_delay import NodeProcessDelayApp

    # Once receive ``ProcessEvent`` or ``RecvQubitPacket``, the process delay is set to 0.5s
    n1.add_apps(NodeProcessDelayApp(delay=0.5, delay_event_list=(ProcessEvent, RecvQubitPacket) ))

    # Once receive a ``RecvClassicPacket``, the delay is set to 0.1s
    n1.add_apps(NodeProcessDelayApp(delay=0.1, delay_event_list=(RecvClassicPacket,) ))
