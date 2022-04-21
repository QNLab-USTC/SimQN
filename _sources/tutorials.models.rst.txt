Physical models
======================

Physical models are the models to describe qubits or entanglements.
SimQN provides an interface (named ``QuantumModel``) to implement multiple physical models.
Currently, SimQN present 2 models, a full functional qubit model and a high level entanglement model. Both models are the child classes of ``QuantumModel``. By extend ``QuantumModel``, other physical models can be built.

``QuantumModel`` class provides two abstract motheds, ``storage_error_model`` and ``transfer_error_model`` to describe the errors in quantum memory and channels. ``storage_error_model`` takes the storage time ``t`` and other parameters as the input. It change the quantum state accordingly. ``transfer_error_model`` takes the channel length ``length`` and other parameters as the input.

.. toctree::
   :maxdepth: 4

   tutorials.models.qubit
   tutorials.models.epr
   tutorials.models.delay