The entanglement model
==============================

The entanglement model is a high level and simpler model for Bell state entanglements, which is common used in quantum networks. Instead of using matrix, entanglement models uses `fidelity` and other parameters to describe an entanglement. Also, this model provide basic quantum operations including entanglement swapping, distillation and teleportation. The advantage is that it simplifies the evaluation by hiding low-level operations and provides higher performance.

Two entanglement models
--------------------------------

We pre-defined two kinds of entanglements, i.e., the ideal Bell-state entanglement and the Werner state entanglement. Both of these entanglements are implemented from `BaseEntanglement`. That means that other entanglement models can also be produced by extend the original `BaseEntanglement`.

The following codes shows how to produce an entanglement:

.. code-block:: python

    from qns.models.epr import WernerStateEntanglement

    # produce entanglements e1 and e2
    e1 = WernerStateEntanglement(fidelity=0.95, name="e1")
    e2 = WernerStateEntanglement(fidelity=0.95, name="e2")

    # entanglement swapping using e1 and e2
    e3 = e1.swapping(e2)
    print(e3.fidelity)

    # produce entanglements e4 and e5
    e4 = WernerStateEntanglement(fidelity=0.95, name="e4")
    e5 = WernerStateEntanglement(fidelity=0.95, name="e5")

    # produce entanglements e4 and e5
    e6 = e4.swapping(e5)
    print(e6.fidelity)

    # entanglement distillation (purification) using e3 and 36
    e7 = e3.distillation(e6)
    print(e7.fidelity)

Both `WernerStateEntanglement` and `BellStateEntanglement` fix the swapping and distillation model. In `BellStateEntanglement`, the quantum state is the max entangled state :math:`\ket{\Phi^+}`, and the fidelity is fixed to 1 (indicates the max entangled state). The entanglement swapping has probability of success `p_swap`. For the `BellStateEntanglement`, no error is introduced during storing and transmission.

In `WernerStateEntanglement`, the the density matrix is

.. math::
    \rho = w \ket{\Phi^+} \bra{\Phi^+} + \frac{1-w}{4} \mathbb{I}_4,

where `w` is the werner parameter and the fidelity is :math:`f = (3w + 1) / 4`. The entanglement swapping protocol will produce a new entanglement (e3 in the above example), where :math:`w_3 = w_1 w_2`. SimQN adopt the Bennett96 distillation protocol, where the success probability is 

.. math::

   f^2+\frac{2}{3}f(1-f) + \frac{5}{9} (1-f)^2

, and the final fidelity is

.. math::

   f' = \frac{f^2+\frac{1}{9}(1-f)^2}{f^2+\frac{2}{3}f(1-f) + \frac{5}{9} (1-f)^2}

For `WernerStateEntanglement`, the werner parameter will drop during storing in quantum memories or transmitting though quantum channels. After storing for time `t`, the new state will be :math:`w' = w \cdot e^{ - \alpha t}`, where :math:`\alpha` is the decoy parameter (default is 0). Both `t` and :math:`\alpha` are input parameter of the `storage_error_model`.

For transmitting error, the new state will be :math:`w' = w \cdot e^{ - \beta l}`, where :math:`\beta` is the decoy parameter (default is 0) and `l` is the channel length. Both `l` and :math:`\beta` are input parameter of the `transfer_error_model`.

If the error models, swapping protocols and distillation protocols do not fit your need, it is easy to implement your own entanglement model by extend `BaseEntanglement`.

Quantum teleportation
----------------------------

Both models provides the teleportation protocol to transmit a qubit using the entanglement. Also, It is possible to change an entanglement model to two entangled qubits model:

.. code-block:: python

    from qns.models.epr import BellStateEntanglement
    from qns.models.qubit.qubit import Qubit
    from qns.models.qubit.const import QUBIT_STATE_0

    e1 = BellStateEntanglement(fidelity=0.8, name="e1")

    # change BellStateEntanglement model to Qubit model
    q0, q1 = e1.to_qubits()
    print(q0.state)

    # execute teleportation protocol to transmit a Qubit
    q0 = Qubit(QUBIT_STATE_0) # the transmitting qubit
    e1 = BellStateEntanglement(fidelity=0.8, name="e0")

    q2 = e1.teleportion(q0) # The transmitted qubit
    print(q2.measure())

To present errors in storage or transmission, users can build their own entanglement models by implementing the `transfer_error_model` and `storage_error_model`.