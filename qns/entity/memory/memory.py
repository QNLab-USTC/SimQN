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

from typing import List, Optional, Union
from qns.simulator.simulator import Simulator
from qns.simulator.ts import Time
from qns.simulator.event import Event
from qns.models.core.backend import QuantumModel
from qns.entity.entity import Entity
from qns.entity.node.node import QNode


class OutOfMemoryException(Exception):
    """
    The exception that the memory is full
    """
    pass


class QuantumMemory(Entity):
    """
    Quantum memory stores qubits or entangled pairs.

    It has two modes:
        Synchronous mode, users can use the ``read`` and ``write`` function to operate the memory directly without delay
        Asynchronous mode, users can use events to operate memories asynchronously
    """
    def __init__(self, name: str = None, node: QNode = None,
                 capacity: int = 0, decoherence_rate: Optional[float] = 0,
                 store_error_model_args: dict = {}, delay: float = 0):
        """
        Args:
            name (str): its name
            node (QNode): the quantum node that equips this memory
            capacity (int): the capacity of this quantum memory. 0 presents unlimited.
            delay (float): the read and write delay in second
            decoherence_rate (float): the decoherence rate of this memory that will pass to the store_error_model
            store_error_model_args (dict): the parameters that will pass to the store_error_model
        """
        super().__init__(name=name)
        self.node = node
        self.capacity = capacity
        self.delay = delay

        if self.capacity > 0:
            self._storage: List[Optional[QuantumModel]] = [None] * self.capacity
            self._store_time: List[Optional[Time]] = [None] * self.capacity
        else:
            self._storage: List[Optional[QuantumModel]] = []
            self._store_time: List[Optional[Time]] = []
        self._usage = 0

        self.decoherence_rate = decoherence_rate
        self.store_error_model_args = store_error_model_args

    def install(self, simulator: Simulator) -> None:
        return super().install(simulator)

    def _search(self, key: Union[QuantumModel, str, int]) -> int:
        index = -1
        if isinstance(key, int):
            if self.capacity == 0 and key >= 0 and key < self._usage:
                index = key
            elif key >= 0 and key < self.capacity and self._storage[key] is not None:
                index = key
        elif isinstance(key, QuantumModel):
            try:
                index = self._storage.index(key)
            except ValueError:
                pass
        elif isinstance(key, str):
            for idx, qubit in enumerate(self._storage):
                if qubit is None:
                    continue
                if qubit.name == key:
                    return idx
        return index

    def get(self, key: Union[QuantumModel, str, int]) -> Optional[QuantumModel]:
        """
        get a qubit from the memory but without removing it from the memory

        Args:
            key (Union[QuantumModel, str, int]): the key. It can be a QuantumModel object,
                its name or the index number.
        """
        try:
            idx = self._search(key)
            if idx != -1:
                return self._storage[idx]
            else:
                return None
        except IndexError:
            return None

    def get_store_time(self, key: Union[QuantumModel, str, int]) -> Optional[QuantumModel]:
        """
        get the store time of a qubit from the memory

        Args:
            key (Union[QuantumModel, str, int]): the key. It can be a QuantumModel object,
                its name or the index number.
        """
        try:
            idx = self._search(key)
            if idx != -1:
                return self._store_time[idx]
            else:
                return None
        except IndexError:
            return None

    def read(self, key: Union[QuantumModel, str]) -> Optional[QuantumModel]:
        """
        The API for reading a qubit from the memory

        Args:
            key (Union[QuantumModel, str]): the key. It can be a QuantumModel object,
                its name or the index number.
        """
        idx = self._search(key)
        if idx == -1:
            return None

        qubit = self._storage[idx]
        store_time = self._store_time[idx]
        self._usage -= 1

        if self.capacity > 0:
            self._storage[idx] = None
            self._store_time[idx] = None
        else:
            self._storage.pop(idx)
            self._store_time.pop(idx)

        t_now = self._simulator.current_time
        sec_diff = t_now.sec - store_time.sec
        qubit.store_error_model(t=sec_diff, decoherence_rate=self.decoherence_rate, **self.store_error_model_args)
        return qubit

    def write(self, qm: QuantumModel) -> bool:
        """
        The API for storing a qubit to the memory

        Args:
            qm (QuantumModel): the `QuantumModel`, could be a qubit or an entangled pair

        Returns:
            bool: whether the qubit is stored successfully
        """
        if self.is_full():
            return False

        if self.capacity <= 0:
            self._storage.append(qm)
            self._store_time.append(self._simulator.current_time)
        else:
            idx = -1
            for i, v in enumerate(self._storage):
                if v is None:
                    idx = i
                    break
            if idx == -1:
                return False
            self._storage[idx] = qm
            self._store_time[idx] = self._simulator.current_time
        self._usage += 1
        return True

    def is_full(self) -> bool:
        """
        check whether the memory is full
        """
        return self.capacity > 0 and self._usage >= self.capacity

    @property
    def count(self) -> int:
        """
        return the current memory usage
        """
        return self._usage

    def handle(self, event: Event) -> None:
        from qns.entity.memory.event import MemoryReadRequestEvent, MemoryReadResponseEvent, \
                                            MemoryWriteRequestEvent, MemoryWriteResponseEvent
        if isinstance(event, MemoryReadRequestEvent):
            key = event.key
            # operate qubits and get measure results
            result = self.read(key)

            t = self._simulator.tc + self._simulator.time(sec=self.delay)
            response = MemoryReadResponseEvent(node=self.node, result=result, request=event, t=t, by=self)
            self._simulator.add_event(response)
        elif isinstance(event, MemoryWriteRequestEvent):
            qubit = event.qubit
            result = self.write(qubit)
            t = self._simulator.tc + self._simulator.time(sec=self.delay)
            response = MemoryWriteResponseEvent(node=self.node, result=result, request=event, t=t, by=self)
            self._simulator.add_event(response)

    def __repr__(self) -> str:
        if self.name is not None:
            return "<memory "+self.name+">"
        return super().__repr__()
