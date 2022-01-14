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

from typing import List, Optional
import numpy as np

from qns.models.qubit.qubit import Qubit, QState
from qns.models.qubit.gate import H, X, Y, Z, CNOT, U
from qns.models.qubit.const import OPERATOR_PAULI_I, QUBIT_STATE_0, QUBIT_STATE_P


class BaseEntanglement(object):
    """
    This is the base entanglement model
    """
    def __init__(self, fidelity: float = 1, name: Optional[str] = None):
        """
        generate an entanglement with certain fidelity

        Args:
            fidelity (float): the fidelity
            name (str): the entanglement name
        """
        self.fidelity = fidelity
        self.name = name
        self.is_decoherenced = False

    def swapping(self, epr: "BaseEntanglement") -> "BaseEntanglement":
        """
        Use `self` and `epr` to perfrom swapping and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entanglement
        """
        raise NotImplementedError

    def distillation(self, epr: "BaseEntanglement") -> "BaseEntanglement":
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entanglement
        """
        raise NotImplementedError

    def to_qubits(self) -> List[Qubit]:
        """
        Transport the entanglement into a pair of qubits based on the fidelity.
        Suppose the first qubit is [1/sqrt(2), 1/sqrt(2)].H

        Returns:
            A list of two qubits
        """
        if self.is_decoherenced:
            q0 = Qubit(state=QUBIT_STATE_P, name="q0")
            q1 = Qubit(state=QUBIT_STATE_P, name="q1")
            return [q0, q1]
        q0 = Qubit(state=QUBIT_STATE_0, name="q0")
        q1 = Qubit(state=QUBIT_STATE_0, name="q1")
        a = np.sqrt(self.fidelity / 2)
        b = np.sqrt((1 - self.fidelity) / 2)
        qs = QState([q0, q1], state=np.array([[a], [b], [b], [a]]))
        q0.state = qs
        q1.state = qs
        self.is_decoherenced = True
        return [q0, q1]

    def teleportion(self, qubit: Qubit) -> Qubit:
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entanglement
        """
        q1, q2 = self.to_qubits()
        CNOT(qubit, q1)
        H(qubit)
        c0 = qubit.measure()
        c1 = q1.measure()
        if c1 == 1 and c0 == 0:
            X(q2)
        elif c1 == 0 and c0 == 1:
            Z(q2)
        elif c1 == 1 and c0 == 1:
            Y(q2)
            U(q2, 1j * OPERATOR_PAULI_I)
        self.is_decoherenced = True
        return q2

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<entanglement {self.name}>"
        return super().__repr__()
