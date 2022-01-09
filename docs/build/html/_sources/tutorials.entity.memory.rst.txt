Quantum memory: the device to store qubits
==============================================

Quantum memory is an entity that can store qubits. It can be equipped to a quantum nodes:

.. code-block:: python

    from qns.entity.node.node import QNode
    from qns.entity.memory.memory import QuantumMemory

    n1 = QNode("n1") # a quantum node named "n1"
    m = QuantumMemory("m1")
    n1.add_memory(m)

``read`` and ``write`` methods are used to store and get a qubit. The ``read`` methods will use the qubit's name or reference as the keyword to search the qubit.

.. code-block:: python

    q1 = Qubit()
    m.write(q1)
    q2 = m.read()

The memory can have a limited size. ``is_full`` function returns whether the memory is full:

.. code-block:: python

    from qns.entity.node.node import QNode
    from qns.entity.memory.memory import QuantumMemory

    n1 = QNode("n1") # a quantum node named "n1"
    m2 = QuantumMemory("m2", capacity = 10) # a memory can store 10 qubits
    n1.add_memory(m2)

    m2.is_full() # check if the memory is full

Also, storage error can be introduced during storage a qubit. The error is handled in function ``storage_error_model``, which takes the storage time and other parameters as the input. Those parameters shows the memory attributions (such as the coherence time), and they can be set using ``store_error_model_args``. This parameter should be in the directory form.

.. code-block:: python

    from qns.entity.memory.memory import QuantumMemory
    from qns.models.epr import WernerStateEntanglement

    class ErrorEntanglement(WernerStateEntanglement):
        def storage_error_model(self, t: float, **kwargs):
            # storage error will reduce the fidelity 
            t_coh = kwargs.get("t_coh", 1)
            self.w = self.w * np.exp(- t / t_coh)

    # memory error attributions: coherence time is 1 second
    m3 = QuantumMemory("m3", capacity = 10, store_error_model_args = {"t_coh": 1})

    # generate an entanglement and store it
    epr1 = ErrorEntanglement(name="epr1")
    m3.write(epr1)

    # after a while, the fidelity will drop
    epr2 = m3.read("epr1")
