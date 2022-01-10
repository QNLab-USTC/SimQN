Timers and build other entities
====================================

We provides a common API for building other entities in the networks, even if it is an virtual entity. All entities must inherit the ``qns.entity.entity.Entity`` class and implements the ``install`` and ``handle`` methods.

- ``install`` takes the simulator as the input parameter. It can generate some initial events.
- ``handle`` will be called by the events that influence the entity. It takes the event as the input parameter.

An example is the ``Timer`` virtual entity. It will generate a ``TimerEvent`` one-shot or periodically. By passing a ``trigger_func`` function, users can do anything one time or periodically during the simulator. For example, users can log the network status 10 times per second to monitor the network.

The source code of the timer is:

.. code-block:: python

    class Timer(Entity):
        def __init__(self, name: str, start_time: float, end_time: float = 0,
                    step_time: float = 1, trigger_func=None):
            """
            Args:
                name: the timer's name
                start_time (float): the start time of the first event
                end_time (float): the time of the final trigger event.
                    If `end_time` is 0, it will be trigger only once.
                step_time (float): the period of trigger events. Default value is 1 second.
                trigger_func: the function that will be triggered.
            """
            super().__init__(name=name)
            self.start_time = start_time
            self.end_time = end_time
            self.step_time = step_time
            self.trigger_func = trigger_func
    
        def install(self, simulator: Simulator) -> None:
    
            if not self._is_installed:
                self._simulator = simulator
    
                time_list = []
                if self.end_time == 0:
                    time_list.append(Time(sec=self.start_time))
                else:
                    t = self.start_time
                    while t <= self.end_time:
                        time_list.append(t)
                        t += self.step_time
    
                for t in time_list:
                    time = self._simulator.time(sec=t)
                    event = TimerEvent(timer=self, t=time)
                    self._simulator.add_event(event)
                self._is_installed = True
    
        def trigger(self):
            if self.trigger_func is not None:
                self.trigger_func()
            else:
                raise NotImplementedError

The timer will trigger ``triggler_func`` from ``start_time`` to ``end_time``. If ``end_time`` is ``None``, the timer will be triggered only one. Otherwise, it will trigger periodically depending on the ``step_time``. The ``install`` function will calculate all trigger timer and generate related trigger event.

Here is an example of using ``Timer``:

.. code-block:: python

    from qns.simulator.simulator import Simulator
    from qns.entity.timer.timer import Timer

    s = Simulator(0, 10, 1000)

    # the trigger function is print the simulation time
    def trigger_func():
        print(s.current_time)

    # generate the timer and install it with the simulator
    t1 = Timer("t1", 0, 10, 0.5, trigger_func)
    t1.install(s)

    # run the simulation
    s.run()