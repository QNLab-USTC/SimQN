from qns.schedular import Entity, Event, Simulator
from qns.log import log


class TimerEvent(Event):
    def __init__(self, timer):
        self.timer = timer

    def run(self, simulator: Simulator):
        self.timer.run(simulator)


class TimerAllocEvent(Event):
    def __init__(self, timer):
        self.timer = timer

    def run(self, simulator: Simulator):
        self.timer.alloc(simulator)


class Timer(Entity):
    def __init__(self, start_time, end_time, step_time, alloc_time = None, name = None):
        self.step_time = step_time
        self.start_time = start_time
        self.end_time = end_time
        self.alloc_time = alloc_time
        if name is None:
            self.name = id(self)
        else:
            self.name = name

    def install(self, simulator: Simulator):
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
                self.alloc_time_slice = simulator.to_time_slice(self.alloc_time)
                for i in range(self.start_time_slice, self.end_time_slice, self.alloc_time_slice):
                    simulator.add_event(i, TimerAllocEvent(self))
        else:
            simulator.add_event(self.start_time_slice, TimerEvent(self))

    def run(self, simulator: Simulator):
        raise NotImplemented

    def alloc(self, simulator: Simulator):
        start_time_slice = simulator.current_time_slice
        end_time_slice = simulator.current_time_slice + self.alloc_time_slice
        log.debug(f"timer {self} allocate for [{start_time_slice},{end_time_slice}] {self.step_time_slice}")
        for i in range(start_time_slice, end_time_slice, self.step_time_slice):
            simulator.add_event(i, TimerEvent(self))
