Entities in quantum networks
==================================

A quantum network in SimQN consists of several entities. All entities are child class of ``Entity``. ``Entity`` has two interfaces:

- ``install``. This method will initial the entity and generate initial events to the simulator.
- ``handle``. This method will be called in case of related event is happened.

Entities in the quantum networks includes:

.. toctree::
   :maxdepth: 4

   tutorials.entity.node
   tutorials.entity.memory
   tutorials.entity.qchannel
   tutorials.entity.cchannel
   tutorials.entity.other