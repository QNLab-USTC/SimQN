The discrete-event simulator
==============================

The ``qns.simulator`` modules provides a discrete-event driven simulator. The simulator organize many events and invokes these events at a pacific time to drive the simulation. Events are bound to a discrete occur time. We start from introducing the time structure.

Time structure
-------------------------------

The time is discrete in SimQN, that is, the smallest time slot is :math:`1/accuracy`, where ``accuracy`` is the number of time slots per second. In SimQN, the ``accuracy`` can be set to meet the simulation's need. Usually, a larger ``accuracy`` brings more simulation overhead.

The discrete time in SimQN is a ``Time`` object, and it can be described in seconds and number of time slots:

.. code-block:: python

    from qns.simulator.ts import Time

    default_time_accuracy = 1,000,000

    t1 = Time(1) # time slot 1, a.k.a 1/1,000,000 second
    t2 = Time(sec=1.1) # time 1.1 seconds, a.k.a 1,100,000 time slots

    print(t1.sec) # output: 1e-6

Also, ``Time`` is comparable.

.. code-block:: python
    
    assert(t1 < t2)
    assert(t1 <= t2)

    t3 = Time(1,100,000)
    assert(t1 == t3)

Events in simulation
--------------------------

``Event`` has a occur time ``t`` and an ``invoke`` function. The ``invoke`` function will be called at time ``t``. Just like ``Time``, ``Event``s are also comparable based on the occur time. ``Event`` object has also an optional attribution ``by`` to represent the entity that generates this event.

.. code-block:: python

    from qns.simulator.event import Event

    # PrintEvent will print "event happened" if invoked
    class PrintEvent(Event):
        def invoke(self) -> None:
            print("event happened")

    # te will happen at 1 second
    te = PrintEvent(t=Time(sec=1), name="test event", by = None)

    # get te's occur time
    print(te.t)

    # invoke the event manually
    te.invoke() # invoke the event

    # cannel the event
    te.cancel() # cancel the event
    assert(te.is_cancelled == True)

    # The events are comparable
    te2 = PrintEvent(t=Time(sec=2), name="test event 2")
    assert(te < te2)

To make it easier of building an event, function ``func_to_event`` can wrap any functions to an event.

.. code-block:: python

    from qns.simulator.event import Event, func_to_event

    # this is a function to print message
    def print_msg(msg):
        print(msg)

    # func_to_event wrap the print_msg to an event. It is invoked at 6 seconds, and the msg is "hello, world"
    print_event = func_to_event(Time(sec = 6, print_msg, "hello, world"))

The Simulator
---------------------

The simulator maintains an event pool that can get the most recent event in order, then the simulator invokes this event. After every events is handled, the simulation finishes. By default, the event pool is implemented from a minimum heap so that getting the most recent event and inserting events can be done quickly.

The simulator is initiated by a start time ``ts``, an end time ``te``, and the optional time accuracy. The simulation will run between ``ts`` and ``te``. During the simulation, the current time is in variable ``tc``.

.. code-block:: python

    # start time is 0 second, end time is 60 seconds.
    s = Simulator(0, 60)

    start_time = s.ts # get the start time
    end_time = s.te # get the end time
    current_time = s.tc # get the current time
    
It is possible to insert an event to the simulator by method ``add_event``, and the simulation can start by method ``run``

.. code-block:: python

    # start time is 0 second, end time is 60 seconds.
    s = Simulator(0, 60)

    print_event = func_to_event(Time(sec = 6, print_msg, "hello, world"))

    # add a new event
    s.add_event(print_event)

    # run the simulation
    s.run()
