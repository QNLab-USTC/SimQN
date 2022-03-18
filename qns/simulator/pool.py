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
from qns.simulator.ts import Time
from qns.simulator.event import Event


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
