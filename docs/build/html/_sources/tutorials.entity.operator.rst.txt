Quantum operator: operating and measuring qubits
==================================================

The quantum operator is designed to represent a quantum circuits, or a group of quantum gates and measurements. Quantum operators can be also used to represent operation errors (using a serial of quantum gates) and the time delay during the measurements or operations.

Quantum operator has two modes: the synchronous and asynchronous mode. In synchronous model, it can not describe the time delay in operating qubits. While in asynchronous mode, quantum operators works as an independent entity. Quantum nodes uses events to control the operator and get the measuring results.

``QuantumOperator`` has the following initiate parameters:

- node, the quantum node that equips this operator
- gate, it is a function to represent the quantum circuits. Its input is one or multiple qubits, and it returns a list of measurement results.
- delay, the time delay of this operator. ``delay`` can be a float or a ``DelayModel``.
- name, the name of this operator

Here is an example of the quantum operator in synchronous mode:

.. code-block:: python

    def gate_z_and_measure(qubit: Qubit):
        # first perform Hadamard gate to the qubit, and then measure the qubit
        H(qubit=qubit)
        result = qubit.measure()
        return result


    n1 = QNode("n1")
    o1 = QuantumOperator(name="o1", node=n1, gate=gate_z_and_measure)

    # add_operator can be used to equip the node with the operator
    n1.add_operator(o1)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    qubit = Qubit()
    ret = o1.operate(qubit)
    assert(ret in [0, 1])

    s.run()

Operators' ``operate`` function can perform the circuits to the input qubits in synchronous mode.

Asynchronous mode
-----------------------

In the asynchronous mode, quantum nodes will use ``OperateRequestEvent`` to active the operator, and listen to the ``OperateResponseEvent`` to get the measure result. In detail, ``OperateRequestEvent.qubits`` is a list of the input qubits, and ``OperateResponseEvent.result`` delivers the measure result. Here is an example of the asynchronous mode. The time delay is set to 0.5s, and an application ``RecvOperateApp`` is installed on the node to listen to and handle the ``OperateResponseEvent``.

.. code-block:: python

    class RecvOperateApp(Application):
        def __init__(self):
            super().__init__()
            self.add_handler(self.OperateResponseEventhandler, [OperateResponseEvent], [])

        def OperateResponseEventhandler(self, node, event: Event) -> Optional[bool]:
            result = event.result
            assert(self._simulator.tc.sec == 0.5)
            assert(result in [0, 1])

    n1 = QNode("n1")
    o1 = QuantumOperator(name="o1", node=n1, gate=gate_z_and_measure, delay=0.5)

    n1.add_operator(o1)
    a1 = RecvOperateApp()
    n1.add_apps(a1)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    qubit = Qubit()
    request = OperateRequestEvent(o1, qubits=[qubit], t=s.time(sec=0), by=n1)
    s.add_event(request)

    s.run()
