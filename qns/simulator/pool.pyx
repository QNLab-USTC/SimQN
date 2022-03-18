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
import numpy as np

cdef class HeapPool(object):
    cdef int size
    cdef int capacity
    cdef list heap

    def __cinit__(self, length=102400):
        self.size = 0
        self.capacity = length
        self.heap = [None]*length

    cdef _get_parent_idx(self, int child_idx):
        cdef int parent_idx
        if child_idx == 0:
            return 0
        if child_idx % 2 == 0:
            parent_idx = int(child_idx / 2 - 1)
        else:
            parent_idx = int(np.floor(child_idx / 2))
        return parent_idx

    cdef get_parent(self, int child_idx):
        parent_idx = self._get_parent_idx(child_idx)
        return self.heap[parent_idx]

    cpdef heappush(self, key):
        cdef int new_size = self.size + 1
        cdef int idx = self.size
        if new_size >= self.capacity:
            self.heap.extend([None]*self.capacity)
            self.capacity *= 2

        self.heap[idx] = key
        cdef int parent_idx = self._get_parent_idx(idx)
        while self.heap[idx] < self.heap[parent_idx]:
            self.heap[parent_idx], self.heap[idx] = self.heap[idx], self.heap[parent_idx]
            idx = parent_idx
            parent_idx = self._get_parent_idx(idx)
        self.size = new_size

    cdef _get_left_child_idx(self, int parent_idx):
        return 2 * parent_idx + 1

    cdef _get_right_child_idx(self, int parent_idx):
        return 2 * parent_idx + 2

    cdef _get_left_child(self, int parent_idx):
        left_child = self.heap[self._get_left_child_idx(parent_idx)]
        return left_child

    cdef _get_right_child(self, int parent_idx):
        right_child = self.heap[self.get_right_child_idx(parent_idx)]
        return right_child

    cdef _get_children_idx(self, int parent_idx):
        return 2 * parent_idx + 1, 2 * parent_idx + 2

    cdef _get_children(self, int parent_idx):
        child_1_idx, child_2_idx = self._get_children_idx(parent_idx)
        return self.heap[child_1_idx], self.heap[child_2_idx]

    cpdef heappop(self):
        root = self.heap[0]
        self.size -= 1
        self.heap[0] = self.heap[self.size]
        self.heap[self.size] = None

        cdef int key_idx = 0
        cdef int c1_idx = self._get_left_child_idx(key_idx)
        cdef int c2_idx = self._get_right_child_idx(key_idx)

        if c1_idx >= self.size or c2_idx >= self.size:
            return root
        # Bubble down root until heap property restored
        while self.heap[key_idx] > self.heap[c1_idx] or self.heap[key_idx] > self.heap[c2_idx]:
            if self.heap[c1_idx] >= self.heap[c2_idx]:
                smaller_child_idx = c2_idx
            else:
                smaller_child_idx = c1_idx

            self.heap[key_idx], self.heap[smaller_child_idx] = self.heap[smaller_child_idx], self.heap[key_idx]

            key_idx = smaller_child_idx
            c1_idx = self._get_left_child_idx(key_idx)
            c2_idx = self._get_right_child_idx(key_idx)
            if c1_idx >= self.size or c2_idx >= self.size:
                break

        return root


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
        self.event_list = HeapPool()

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

        self.event_list.heappush(event)
        return True

    def next_event(self) -> Event:
        '''
        Get the next event to be executed

        Returns:
            The next event to be executed
        '''
        try:
            event: Event = self.event_list.heappop()
            if event is None:
                self.tc = self.te
            else:
                self.tc = event.t
        except IndexError:
            event = None
            self.tc = self.te
        return event
