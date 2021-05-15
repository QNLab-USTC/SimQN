from qns.schedular import Entity, Event, Simulator

class Timer(Entity):
    def __init__(self, start_time, end_time, step_time):
        self.step_time = step_time
        self.start_time =start_time
        self.end_time = end_time

    def install(self, simulator: Simulator):
        if self.step_time is not None:
            self.step_time_slice = simulator.to_time_slice(self.step_time)
        if self.end_time is not None:
            self.end_time_slice = simulator.to_time_slice(self.end_time)
        self.start_time_slice = simulator.to_time_slice(self.start_time)

        class TimerEvent(Event):
            def __init__(self, timer):
                self.timer = timer

            def run(self, simulator: Simulator):
                self.timer.run(simulator)

        if self.end_time_slice is not None and self.step_time_slice is not None:
            for i in range(self.start_time_slice, self.end_time_slice, self.step_time_slice):
                simulator.add_event(i, TimerEvent(self))
        else:
            simulator.add_event(self.start_time_slice, TimerEvent(self))
    
    def run(self, simulator: Simulator):
        raise NotImplemented