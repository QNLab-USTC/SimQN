#    SimQN: a discrete-event simulator for the quantum networks
#    Copyright (C) 2021-2022 Lutong Chen, Jian Li, Kaiping Xue
#    University of Science and Technology of China, USTC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Any, Optional
from qns.simulator.simulator import Simulator
from qns.simulator.event import Event
from qns.simulator.ts import Time
from qns.entity.entity import Entity


class Timer(Entity):
    """
    A `Timer` is an `Entity` that trigger the function `trigger_func` one-shot or periodically.
    """
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
                event = TimerEvent(timer=self, t=time, by=self)
                self._simulator.add_event(event)
            self._is_installed = True

    def trigger(self):
        if self.trigger_func is not None:
            self.trigger_func()
        else:
            raise NotImplementedError


class TimerEvent(Event):
    """
    TimerEvent is the event that triggers the Timer's `trigger_func`
    """
    def __init__(self, timer: Timer, t: Optional[Time] = None, name: Optional[str] = None, by: Optional[Any] = None):
        super().__init__(t=t, name=name, by=by)
        self.timer = timer

    def invoke(self) -> None:
        self.timer.trigger()
