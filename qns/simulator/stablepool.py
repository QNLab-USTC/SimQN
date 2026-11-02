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


class StableEventPool(object):
    class StableEvent:
        def __init__(self, event: Event, seq: int) -> None:
            self.event = event
            self.seq = seq

        def __eq__(self, other) -> bool:
            return self.event == other.event and self.seq == other.seq

        def __lt__(self, other) -> bool:
            return self.event < other.event or (
                self.event == other.event and self.seq < other.seq
            )

        def __le__(self, other) -> bool:
            return self < other or self == other

        def __gt__(self, other) -> bool:
            return not (self < other or self == other)

        def __ge__(self, other) -> bool:
            return not (self < other)

        def __ne__(self, other) -> bool:
            return not self == other

    """
    The default implement of the event pool
    """

    def __init__(self, ts: Time, te: Time):
        """
        Args:
            ts: the start time
            te: the end time
        """
        self.ts = ts
        self.te = te
        self.tc = ts
        self.event_list = []
        self.seq = 0

    @property
    def current_time(self) -> Time:
        """
        Get the current time
        """
        return self.tc

    @property
    def min_time(self) -> Time:
        """
        Get the minimum time in the pool
        """
        if self.event_list:
            return self.event_list[0].event.t   # 堆顶 = 最小
        return self.te                    # 空 → 返回结束时间（相当于 ∞）
    
    def add_event(self, event: Event) -> bool:
        """
        Insert an event into the pool

        Args:
            event (Event): The inserting event
        Returns:
            if the event is inserted successfully
        """
        if event.t < self.tc or event.t > self.te:
            return False

        sevent = self.StableEvent(event, self.seq)
        self.seq += 1
        heapq.heappush(self.event_list, sevent)
        return True

    def next_event(self) -> Event:
        """
        Get the next event to be executed

        Returns:
            The next event to be executed
        """
        try:
            sevent = heapq.heappop(self.event_list)
            event = sevent.event
            self.tc = event.t
        except IndexError:
            event = None
            self.tc = self.te
        return event
