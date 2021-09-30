from typing import Optional
from qns.simulator import Simulator, Event, Time
from qns.entity import Entity

class Timer(Entity):
    """
    A `Timer` is an `Entity` that trggle the function `triggle_func` one-shot or preiodly.
    """
    def __init__(self, name: str, start_time: float, end_time: float = 0, step_time: float = 1, triggle_func = None):
        """
        Args:
            name: the timer's name
            start_time (float): the start time of the first event
            end_time (float): the time of the final triggle event. If `end_time` is 0, it will be triggle only once.
            step_time (float): the period of triggling events. Default value is 1 second.
            triggle_func: the function that will be triggled.
        """
        super().__init__(name=name)
        self.start_time = start_time
        self.end_time = end_time
        self.step_time = step_time
        self.triggle_func = triggle_func

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
                time = self._simulator.time(sec = t)
                event = TimerEvent(timer = self, t = time)
                self._simulator.add_event(event)
            self._is_installed = True

    def triggle(self):
        if self.triggle_func is not None:
            self.triggle_func()
        else:
            raise NotImplemented

class TimerEvent(Event):
    """
    TimerEvent is the event that triggles the Timer's `triggle_func`
    """
    def __init__(self, timer: Timer, t: Optional[Time] = None, name: Optional[str] = None):
        super().__init__(t=t, name=name)
        self.timer = timer
        
    def invoke(self) -> None:
        self.timer.triggle()