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

import heapq
import time
from typing import Optional
from qns.simulator.ts import Time, default_accuracy
from qns.simulator.event import Event
import qns.utils.log as log
from . import ts

default_start_second = 0.0
default_end_second = 60.0


class Simulator(object):
    """
    The discrete-event driven simulator core
    """

    def __init__(self, start_second: float = default_start_second,
                 end_second: float = default_end_second,
                 accuracy: int = default_accuracy):
        """
        Args:
            start_second (float): the start second of the simulation
            end_second (float): the end second of the simulation
            accuracy (int): the number of time slots per second
        """
        self.accuracy = accuracy
        ts.default_accuracy = accuracy

        self.ts: Time = self.time(sec=start_second)
        self.te: Time = self.time(sec=end_second)
        self.time_spend: float = 0

        self.event_pool = DefaultEventPool(self.ts, self.te)
        self.status = {}
        self.total_events = 0

    @property
    def current_time(self) -> Time:
        '''
        Get the current time of the simulation

        Returns:
            (Time) the current time
        '''
        return self.event_pool.current_time

    @property
    def tc(self) -> Time:
        """
        The alias of `current_time`
        """
        return self.current_time

    def time(self, time_slot: Optional[int] = None, sec: Optional[float] = None) -> Time:
        """
        Produce a ``Time`` using ``time_slot`` or ``sec``

        Args:
            time_slot (Optional[int]): the time slot
            sec (Optional[float]): the second
        Returns:
            the produced ``Time`` object
        """
        if time_slot is not None:
            return Time(time_slot=time_slot, accuracy=self.accuracy)
        return Time(sec=sec, accuracy=self.accuracy)

    def add_event(self, event: Event) -> None:
        '''
        Add an ``event`` into simulator event pool.
        :param event: the inserting event
        '''
        if self.event_pool.add_event(event):
            self.total_events += 1

    def run(self) -> None:
        '''
        Run the simulate
        '''
        log.debug("simulation started.")

        trs = time.time()
        event = self.event_pool.next_event()
        while event is not None:
            if not event.is_canceled:
                event.invoke()
            event = self.event_pool.next_event()

        tre = time.time()
        self.time_spend = tre - trs
        log.debug("simulation finished.")

        if tre - trs == 0:
            log.debug(f"runtime {tre - trs}, {self.total_events} events,\
                sim_time {self.te.sec - self.ts.sec}, xINF")
        else:
            log.debug(f"runtime {tre - trs}, {self.total_events} events,\
                sim_time {self.te.sec - self.ts.sec}, x{(self.te.sec - self.ts.sec)/(tre-trs)}")


class DefaultEventPool(object):
    """
    The default implement of the event pool
    """

    def __init__(self, ts: Time, te: Time):
        '''
        Args:
            ts: the start time
            te: the end time
        '''
        self.ts = ts
        self.te = te
        self.tc = ts
        self.event_list = []

    @property
    def current_time(self) -> Time:
        '''
        Get the current time
        '''
        return self.tc

    def add_event(self, event: Event) -> bool:
        '''
        Insert an event into the pool

        Args:
            event (Event): The inserting event
        Returns:
            if the event is inserted successfully
        '''
        if event.t < self.tc or event.t > self.te:
            return False

        heapq.heappush(self.event_list, event)
        return True

    def next_event(self) -> Event:
        '''
        Get the next event to be executed

        Returns:
            The next event to be executed
        '''
        try:
            event: Event = heapq.heappop(self.event_list)
            self.tc = event.t
        except IndexError:
            event = None
            self.tc = self.te
        return event
