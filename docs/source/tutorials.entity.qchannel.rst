Quantum channel: the link to transmit qubits
================================================

Quantum channels can transmit a ``QuantumModel`` (qubit) from a node to another.
It has the following attributions:

- ``name``: the channel's name.
- ``length``: the physcial length of the channel. Default length is 0
- ``delay``: the propagation delay. The time delay from sending to receiving. ``delay`` can be a float or a ``DelayModel``. Default delay is 0s.
- ``drop_rate``: the probability of losing the transmitting qubit. Default drop rate is 0.
- ``bandwidth``: the number of qubits to be sent per second. If the ``bandwidth`` is reached, further qubits will be put into a buffer (and causes a buffer delay). Default bandwidth is ``None`` (infinite).
-  ``max_buffer_size``: the maximum send buffer size. If the buffer is full, further qubits will be dropped. Default buffer size is ``None`` (infinite).
- ````decoherence_rate``: the decoherence rate, have different meanings in qubit or entanglement models.
- ``transfer_error_model_args``: other attributions for the error model.

It is easy to generate a quantum channel:

.. code-block:: python

    from qns.entity.node.node import QNode
    from qns.entity.qchannel.qchannel import QuantumChannel

    n2 = QNode("n2")
    n1 = QNode("n1")
    l1 = QuantumChannel(name="l1", bandwidth=3, delay=0.2, drop_rate=0.1, max_buffer_size=5)

    # add the qchannel
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)

    # get_qchannel can return the quantum channel by its destination
    assert(l1 == n1.get_qchannel(n2))

    s = Simulator(0, 10, 1000)
    # install QNodes will also install all channels
    n1.install(s)
    n2.install(s)
    s.run()


Send and receive qubits
----------------------------------------

It is easy to send a qubit using ``send`` method:

.. code-block:: python

    n1 = QNode("n1")
    n2 = QNode("n2")

    l1 = QuantumChannel(name="l1")
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)

    # install and initiate the simulator
    # ...

    qubit = Qubit()

    # use the send method to send qubit
    l1.send(qubit = qubit, next_hop = n2)

The receiving may be complex. The destination node will be noticed by an event called ``RecvQubitPacket``. It has the following fields:

- ``t``: the receiving time
- ``qchannel``: the related quantum channel
- ``qubit``: the receiving qubit
- ``dest``: the destination

This packet needs to be processed in the ``handle`` method of the applications:

.. code-block:: python

    class SendApp(Application):
        def __init__(self, dest: QNode, qchannel: QuantumChannel, send_rate=1000):
            super().__init__()
            self.dest = dest
            self.qchannel = qchannel
            self.send_rate = send_rate

        # initiate: generate the first send event
        def install(self, node: QNode, simulator: Simulator):
            super().install(node, simulator)

            # get start time
            time_list.append(simulator.ts)

            t = simulator.ts
            event = func_to_event(t, self.send_qubit)
            self._simulator.add_event(event)

        def send_qubit(self):
            # generate a qubit
            qubit = Qubit()

            # send the qubit
            self.qchannel.send(qubit=qubit, next_hop=self.dest)

            # calculate the next sending time
            t = self._simulator.current_time + \
                self._simulator.time(sec=1 / self.send_rate)
            
            # insert the next send event to the simulator
            event = func_to_event(t, self.send_qubit)
            self._simulator.add_event(event)

    class RecvApp(Application):
        def handle(self, node: QNode, event: Event):
            if isinstance(event, RecvQubitPacket):
                qubit = event.qubit
                qchannel = event.qchannel
                recv_time = event.t

                # handling the receiving qubit
                # ...

    # generate quantum nodes
    n1 = QNode("n1")
    n2 = QNode("n2") # add the RecvApp

    # generate a quantum channel
    l1 = QuantumChannel(name="l1")
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)

    # add apps
    n1.add_apps(SendApp(dest = n2, qchannel = l1))
    n2.add_apps(RecvApp())

    # initiate the simulator 
    s = Simulator(0, 10, 10000) # from  0 to 10 seconds
    n1.install(s)
    n2.install(s)

    # run the simulation
    s.run()

Error models in transmission
-------------------------------

Errors can be introduced during sending qubits. The error is handled in function ``transfer_error_model``, which takes the channel ``length`` and other parameters as input. Those parameters shows the quantum channel's attributions (such as the optical fiber's decay), and they can be set using ``transfer_error_model_args``. This parameter should be in the directory form.

Here is an example:

.. code-block:: python

    # Extend the qubit model to handle transfer error
    class QubitWithError(Qubit):
        def transfer_error_model(self, length: float, **kwargs):

            # get the decay attribution
            decay = kwargs.get("decay", 0)

            # handle error
            lkm = length / 1000
            theta = random.random() * lkm * decay * np.pi / 4
            operation = np.array([[np.cos(theta), - np.sin(theta)], [np.sin(theta), np.cos(theta)]], dtype=np.complex128)

            # change the state vector
            self.state.state = np.dot(operation, self.state.state)

    n1 = QNode("n1")
    n2 = QNode("n2")

    # the error model attribution: decay 0.2db/KM
    l1 = QuantumChannel(name="l1", transfer_error_model_args={"decay": 0.2})
    n1.add_qchannel(l1)
    n2.add_qchannel(l1)

    # generate a qubit in ``QubitWithError`` model
    qubit = QubitWithError()

    # send the qubit
    l1.send(qubit=qubit, next_hop=n2)

Qubit Loss Quantum Channel
-------------------------------

``qns.entity.qchannel.QubitLossChannel`` is a usually used quantum channel model, that it will drop qubits randomly, following this possibility: :math:`1-(1-p_{\text{init}})*10^{- \miu \cdot length / 10}`, where :math:`p_{\text{init}}` is the initial drop probability of generating a qubit, :math:`\miu` is the attenuation rate, and :math"`length` is the channel length.