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

from typing import Callable, List, Optional, Union
from qns.entity.entity import Entity
from qns.entity.node.node import QNode
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator


class QuantumOperator(Entity):
    """
    Quantum operator can perfrom quantum operation or measurements on qubits.
    It has two modes:
        Synchronous mode, users can use the `operate` function to operate qubits directly without delay
        Asynchronous mode, users will use events to operate quantum operations asynchronously
    """

    def __init__(self, name: str = None, node: QNode = None,
                 gate: Callable[..., Union[None, int, List[int]]] = None, delay: float = 0):
        """

        Args:
            name (str): its name
            node (QNode): the quantum node that equips this memory
            gate: the quantum circuit where the input is the operating qubits and returns the measure result
            delay (float): the delay time in second for this operation
        """
        super().__init__(name=name)
        self.node = node
        self.gate = gate
        self.delay = delay

    def install(self, simulator: Simulator) -> None:
        return super().install(simulator)

    def handle(self, event: Event) -> None:
        from qns.entity.operator.event import OperateRequestEvent, OperateResponseEvent
        if isinstance(event, OperateRequestEvent):
            qubits = event.qubits
            # operate qubits and get measure results
            result = self.operate(*qubits)

            t = self._simulator.tc + self._simulator.time(sec=self.delay)
            response = OperateResponseEvent(node=self.node, result=result, request=event, t=t, by=self)
            self._simulator.add_event(response)

    def set_own(self, node: QNode):
        """
        set the owner of this quantum operator
        """
        self.node = node

    def operate(self, *qubits) -> Optional[Union[int, List[int]]]:
        """
        operate on qubits and return the measure result

        Args:
            qubits: the operating qubits

        Returns:
            the measure result
        """
        return self.gate(*qubits)
