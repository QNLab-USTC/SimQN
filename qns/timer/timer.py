from qns.schedular import Entity, Event, Simulator
from qns.log import log
import uuid


class TimerEvent(Event):
    def __init__(self, timer):
        self.timer = timer

    def run(self, simulator: Simulator):
        '''
        This is an inner event that triggle ``Timer``'s ``run`` function.
        '''
        self.timer.run(simulator)


class TimerAllocEvent(Event):
    def __init__(self, timer):
        self.timer = timer

    def run(self, simulator: Simulator):
        '''
        This is an inner event that triggle ``Timer``'s ``alloc`` function.
        '''
        self.timer.alloc(simulator)


class Timer(Entity):
    '''
    Timer is a virtual entity that triggle a ``TimerEvent`` ine-time or periodly.

    If both ``step_time`` and ``end_time`` is not ``None``, the timer will call ``TimerEvent`` periodly.
    Or it will only triggle once at ``start_time``.

    There will be a great overhead if every ``TimerEvent`` is generated before the simulator runs.
    Setting an appropriate ``alloc_time`` can effectively reduce the initialization time.

    :param float start_time: The timer's start time in second
    :param float end_time: The timer's finish time in second
    :param float step_time: The ``TimerEvent`` will be called every ``step_time``
    :param float alloc_time: The next ``TimerEvent`` will be generated and inserted into simulator every ``alloc_time``
    :param str name: timer's name
    '''

    def __init__(self, start_time, end_time=None, step_time=None, alloc_time=1, name=None):
        self.step_time = step_time
        self.start_time = start_time
        self.end_time = end_time
        self.alloc_time = alloc_time
        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

    def install(self, simulator: Simulator):
        '''
        This function runs before simulator is started. It is used to inject initial ``TimerEvent``s.
        '''
        if self.step_time is not None:
            self.step_time_slice = simulator.to_time_slice(self.step_time)
        if self.end_time is not None:
            self.end_time_slice = simulator.to_time_slice(self.end_time)
        self.start_time_slice = simulator.to_time_slice(self.start_time)

        if self.end_time_slice is not None and self.step_time_slice is not None:
            if self.alloc_time is None:
                for i in range(self.start_time_slice, self.end_time_slice, self.step_time_slice):
                    simulator.add_event(i, TimerEvent(self))
            else:
                self.alloc_time_slice = simulator.to_time_slice(
                    self.alloc_time)
                for i in range(self.start_time_slice, self.end_time_slice, self.alloc_time_slice):
                    simulator.add_event(i, TimerAllocEvent(self))
        else:
            simulator.add_event(self.start_time_slice, TimerEvent(self))

    def run(self, simulator: Simulator):
        '''
        This function must be overrided to perform specific functions.

        :param simulator: the simulator
        '''
        raise NotImplemented

    def alloc(self, simulator: Simulator):
        start_time_slice = simulator.current_time_slice
        end_time_slice = simulator.current_time_slice + self.alloc_time_slice
        log.debug(
            f"timer {self} allocate for [{start_time_slice},{end_time_slice}] {self.step_time_slice}")
        for i in range(start_time_slice, end_time_slice, self.step_time_slice):
            simulator.add_event(i, TimerEvent(self))
