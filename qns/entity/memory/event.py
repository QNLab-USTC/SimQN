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


from typing import Optional, Union
from qns.entity.node.node import QNode
from qns.models.core.backend import QuantumModel
from qns.simulator.event import Event
from qns.simulator.ts import Time


class MemoryReadRequestEvent(Event):
    """
    ``MemoryReadRequestEvent`` is the event that request a memory read
    """
    def __init__(self, memory, key: Union[QuantumModel, str],
                 t: Optional[Time] = None, name: Optional[str] = None):
        super().__init__(t=t, name=name)
        self.memory = memory
        self.key = key

    def invoke(self) -> None:
        self.memory.handle(self)


class MemoryReadResponseEvent(Event):
    """
    ``MemoryReadResponseEvent`` is the event that returns the memory read result
    """
    def __init__(self, node: QNode, result: Optional[QuantumModel] = None,
                 request: MemoryReadRequestEvent = None, t: Optional[Time] = None, name: Optional[str] = None):
        super().__init__(t=t, name=name)
        self.node = node
        self.result = result
        self.request = request

    def invoke(self) -> None:
        self.node.handle(self)


class MemoryWriteRequestEvent(Event):
    """
    ``MemoryWriteRequestEvent`` is the event that request a memory write
    """
    def __init__(self, memory, qubit: QuantumModel,
                 t: Optional[Time] = None, name: Optional[str] = None):
        super().__init__(t=t, name=name)
        self.memory = memory
        self.qubit = qubit

    def invoke(self) -> None:
        self.memory.handle(self)


class MemoryWriteResponseEvent(Event):
    """
    ``MemoryWriteResponseEvent`` is the event that returns the memory write result
    """
    def __init__(self, node: QNode, result: Optional[QuantumModel] = None,
                 request: MemoryReadRequestEvent = None, t: Optional[Time] = None, name: Optional[str] = None):
        super().__init__(t=t, name=name)
        self.node = node
        self.result = result
        self.request = request

    def invoke(self) -> None:
        self.node.handle(self)
