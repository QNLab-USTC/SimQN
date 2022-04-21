Delay model
==============================

Delay model can be used to describe a random time delay in channels, memories and operators. The basic class is ``DelayModel``.
It implements a method called ``calculate`` to calculate the random time delay.

Currently, SimQN provides the following three delay models:

1. ConstantDelayModel: generate a constant time delay

.. code-block:: python

    from qns.models.delay import ConstantDelayModel

    delay_model = ConstantDelayModel(delay=0.5) # set time delay to a constant number 0.5 [s]

    delay = delay_model.calculate() # output: 0.5

2. UniformDelayModel: generate a random delay in uniform distribution X~U(min, max)

.. code-block:: python

    from qns.models.delay import UniformDelayModel

    delay_model = UniformDelayModel(min_delay=0.3, max_delay=0.5) # set time delay to a random delay

    delay = delay_model.calculate() # output: 0.44

3. NormalDelayModel: generate a random delay in normal distribution X~N(mean_delay, std)

.. code-block:: python

    from qns.models.delay import NormalDelayModel

    delay_model = NormalDelayModel(mean_delay=0.5, std=0.1) # set time delay to a random delay in normal distribution

    delay = delay_model.calculate() # output: 0.44

Usages: a ``DelayModel`` can be a input parameters in quantum memories, quantum channels, classic channels and operators, for example:

.. code-block:: python

    from qns.models.delay import NormalDelayModel
    from qns.entity.cchannel import ClassicChannel

    l1 = ClassicChannel(name="l1", bandwidth=10, delay=UniformDelayModel(min_delay=0.1, max_delay=0.3),
                        drop_rate=0.1, max_buffer_size=30)