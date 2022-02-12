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
from qns.entity.timer.timer import Timer
from qns.models.core.backend import QuantumModel
from qns.simulator.event import Event
from qns.simulator.ts import Time


class OperateRequestEvent(Event):
    """
    ``OperateRequestEvent`` is the event that request a operator to handle
    """
    def __init__(self, operator, qubits: list[QuantumModel] = [],
                 t: Optional[Time] = None, name: Optional[str] = None):
        super().__init__(t=t, name=name)
        from qns.entity.operator.operator import QuantumOperator
        self.operator: QuantumOperator = operator
        self.qubits = qubits

    def invoke(self) -> None:
        self.operator.handle(self)


class OperateResponseEvent(Event):
    """
    ``OperateResponseEvent`` is the event that returns the operating result
    """
    def __init__(self, node: QNode, result: Union[int, list[int]] = None,
                 t: Optional[Time] = None, name: Optional[str] = None):
        super().__init__(t=t, name=name)
        self.node = node
        self.result = result

    def invoke(self) -> None:
        self.node.handle(self)