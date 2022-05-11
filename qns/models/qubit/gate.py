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
import numpy as np
from qns.models.qubit.const import OPERATOR_HADAMARD, OPERATOR_PAULI_I,\
                                   OPERATOR_PAULI_X, OPERATOR_PAULI_Y, \
                                   OPERATOR_PAULI_Z, OPERATOR_PHASE_SHIFT,\
                                   OPERATOR_RX, OPERATOR_RY, OPERATOR_RZ,\
                                   OPERATOR_S, OPERATOR_T
from qns.models.qubit.qubit import Qubit
from qns.models.qubit.utils import kron, joint
from qns.models.qubit.errors import QGateOperatorNotMatchError, QGateQubitNotInStateError


class Gate():
    """
    The quantum gates that will operate qubits
    """

    def __init__(self, name: Optional[str] = None, _docs: Optional[str] = None):
        """
        Args:
            name (str): the gate's name
        """
        self._name: Optional[str] = name
        self.__doc__ = _docs

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        pass


class SingleQubitGate(Gate):
    """
    The single qubit gates operate on a single qubit
    """

    def __init__(self, name: Optional[str] = None, operator: Optional[np.ndarray] = None, _docs: Optional[str] = None):
        """
        Args:
            name (str): the gate's name
            operator (np.ndarray): the matrix represent of this operator
        """
        super().__init__(name, _docs)
        self._operator = operator

    def __call__(self, qubit: Qubit) -> None:
        """
        Args:
            qubit (Qubit): the operating qubit

        Raises:
            QGateOperatorNotMatchError
            QGateQubitNotInStateError
        """
        qubit.operate(self._operator)


X = SingleQubitGate(name="X", operator=OPERATOR_PAULI_X, _docs="Pauli X Gate")
Y = SingleQubitGate(name="Y", operator=OPERATOR_PAULI_Y, _docs="Pauli Y Gate")
Z = SingleQubitGate(name="Z", operator=OPERATOR_PAULI_Z, _docs="Pauli Z Gate")
I = SingleQubitGate(name="I", operator=OPERATOR_PAULI_I, _docs="Pauli I Gate")
H = SingleQubitGate(name="H", operator=OPERATOR_HADAMARD, _docs="Hadamard Gate")
T = SingleQubitGate(name="T", operator=OPERATOR_T, _docs="T gate (pi/4 shift gate)")
S = SingleQubitGate(name="S", operator=OPERATOR_S, _docs="S gate (pi/2 shift gate)")


class SingleQubitRotateGate(SingleQubitGate):
    def __call__(self, qubit: Qubit, theta=np.pi/4) -> None:
        """
        Args:
            qubit (Qubit): the operating qubit
            theta (float): the rotating degree
        Raises:
            QGateOperatorNotMatchError
            QGateQubitNotInStateError
        """
        qubit.operate(self._operator(theta))


R = SingleQubitRotateGate(name="R", operator=OPERATOR_PHASE_SHIFT, _docs="R gate (phase shift gate)")
RX = SingleQubitRotateGate(name="RX", operator=OPERATOR_RX, _docs="Rx gate (X rotate gate)")
RY = SingleQubitRotateGate(name="RY", operator=OPERATOR_RY, _docs="Ry gate (Y rotate gate)")
RZ = SingleQubitRotateGate(name="RZ", operator=OPERATOR_RZ, _docs="Rz gate (Z rotate gate)")


class SingleQubitArbitraryGate(SingleQubitGate):
    def __call__(self, qubit: Qubit, operator: np.ndarray) -> None:
        """
        Args:
            qubit (Qubit): the operating qubit
            operator (np.ndarray): the operator matrix
        Raises:
            QGateOperatorNotMatchError
            QGateQubitNotInStateError
        """
        if operator.shape != (2, 2):
            raise QGateOperatorNotMatchError
        self._operator = operator
        qubit.operate(self._operator)


U = SingleQubitArbitraryGate(name="U", operator=None, _docs="Arbitrary single qubit operation gate")


class DoubleQubitsControlledGate(Gate):
    """
    The double qubits gates operate on two qubits, including a controlled qubit and a operating qubit.

    The controlled  gate:

        [[I_2, 0][0, operator]]
    """

    def __init__(self, name: Optional[str] = None,
                 operator: Optional[np.ndarray] = OPERATOR_PAULI_X, _docs: Optional[str] = None):
        """
        Args:
            name (str): the gate's name
            operator (np.ndarray): the matrix represent of the operator
        """
        super().__init__(name, _docs)
        self._operator = operator

    def __call__(self, qubit1: Qubit, qubit2: Qubit,
                 operator: Optional[np.ndarray] = None) -> None:
        """
        Args:
            qubit1 (Qubit): the first qubit (controller)
            qubit2 (Qubit): the second qubit
            operator (np.ndarray): the matrix represent of the operator

        Raises:
            QGateOperatorNotMatchError
            QGateQubitNotInStateError
            QGateStateJointError
        """
        if operator is None:
            operator = self._operator
        if operator.shape != (2, 2):
            raise QGateOperatorNotMatchError

        if qubit1 == qubit2:
            return
        joint(qubit1, qubit2)
        state = qubit1.state

        try:
            idx1 = state.qubits.index(qubit1)
            idx2 = state.qubits.index(qubit2)
        except ValueError:
            raise QGateQubitNotInStateError

        full_operator_part_0 = np.array([1])  # |0> <0|
        full_operator_part_1 = np.array([1])  # |1> <1|

        for i in range(state.num):
            if i == idx1:
                full_operator_part_0 = kron(full_operator_part_0, np.array([[1, 0], [0, 0]]))
                full_operator_part_1 = kron(full_operator_part_1, np.array([[0, 0], [0, 1]]))
            elif i == idx2:
                full_operator_part_0 = kron(full_operator_part_0, OPERATOR_PAULI_I)
                full_operator_part_1 = kron(full_operator_part_1, operator)
            else:
                full_operator_part_0 = kron(full_operator_part_0, OPERATOR_PAULI_I)
                full_operator_part_1 = kron(full_operator_part_1, OPERATOR_PAULI_I)
        full_operator = full_operator_part_0 + full_operator_part_1
        qubit1.state.operate(full_operator)


ControlledGate = DoubleQubitsControlledGate(name="Controlled Gate",
                                            operator=OPERATOR_PAULI_X, _docs="The controlled gate")
CNOT = DoubleQubitsControlledGate(name="Controlled NOT Gate",
                                  operator=OPERATOR_PAULI_X, _docs="The controlled Pauli-X gate")
CX = DoubleQubitsControlledGate(name="Controlled Pauli-X Gate",
                                operator=OPERATOR_PAULI_X, _docs="The controlled Pauli-X gate")
CY = DoubleQubitsControlledGate(name="Controlled Pauli-Y Gate",
                                operator=OPERATOR_PAULI_Y, _docs="The controlled Pauli-Y gate")
CZ = DoubleQubitsControlledGate(name="Controlled Pauli-Z Gate",
                                operator=OPERATOR_PAULI_Z, _docs="The controlled Pauli-Z gate")


class DoubleQubitsRotateGate(DoubleQubitsControlledGate):
    def __call__(self, qubit1: Qubit, qubit2: Qubit, theta: float = np.pi/4) -> None:
        operator = self._operator(theta)
        super().__call__(qubit1, qubit2, operator=operator)


CR = DoubleQubitsRotateGate(name="Controlled Phase Rotate Gate",
                            operator=OPERATOR_PHASE_SHIFT, _docs="The controlled rotate gate")


class SwapGate(Gate):
    def __call__(self, qubit1: Qubit, qubit2: Qubit):
        """
        The swap gate, swap the states of qubit1 and qubit2

        Args:
            qubit1 (Qubit): the first qubit (controller)
            qubit2 (Qubit): the second qubit

        Raises:
            QGateOperatorNotMatchError
            QGateQubitNotInStateError
        """
        if qubit1 == qubit2:
            return
        joint(qubit1, qubit2)

        state = qubit1.state
        # single qubit operate
        try:
            idx1 = state.qubits.index(qubit1)
            idx2 = state.qubits.index(qubit2)
        except ValueError:
            raise QGateQubitNotInStateError

        state.qubits[idx1], state.qubits[idx2] = state.qubits[idx2], state.qubits[idx1]


Swap = SwapGate(name="Swap Gate", _docs="swap the states of qubit1 and qubit2")


class ThreeQubitsGate(Gate):
    """
    The gate operates on three qubits, including 2 controlled qubit and a operating qubit.

    The 3 controlled-controlled gate:

        [[I_6, 0][0, operator]]
    """
    def __init__(self, name: Optional[str] = None,
                 operator: Optional[np.ndarray] = OPERATOR_PAULI_X, _docs: Optional[str] = None):
        """
        Args:
            name (str): the gate's name
            operator (np.ndarray): the matrix represent of the operator
        """
        super().__init__(name, _docs)
        self._operator = operator

    def __call__(self, qubit1: Qubit, qubit2: Qubit, qubit3: Qubit, operator: Optional[np.ndarray] = None) -> Any:
        if operator is None:
            operator = self._operator
        if operator.shape != (2, 2):
            raise QGateOperatorNotMatchError

        if qubit1 == qubit2 or qubit1 == qubit3 or qubit2 == qubit3:
            return
        joint(qubit1, qubit2)
        joint(qubit2, qubit3)

        state = qubit1.state

        # single qubit operate
        try:
            idx1 = state.qubits.index(qubit1)
            idx2 = state.qubits.index(qubit2)
            idx3 = state.qubits.index(qubit3)
        except ValueError:
            raise QGateQubitNotInStateError

        full_operator_part_00 = np.array([1])  # |0> <0|
        full_operator_part_01 = np.array([1])  # |1> <1|
        full_operator_part_10 = np.array([1])  # |0> <0|
        full_operator_part_11 = np.array([1])  # |1> <1|

        for i in range(state.num):
            if i == idx1:
                full_operator_part_00 = kron(full_operator_part_00, np.array([[1, 0], [0, 0]]))
                full_operator_part_01 = kron(full_operator_part_01, np.array([[1, 0], [0, 0]]))
                full_operator_part_10 = kron(full_operator_part_10, np.array([[0, 0], [0, 1]]))
                full_operator_part_11 = kron(full_operator_part_11, np.array([[0, 0], [0, 1]]))
            elif i == idx2:
                full_operator_part_00 = kron(full_operator_part_00, np.array([[1, 0], [0, 0]]))
                full_operator_part_10 = kron(full_operator_part_10, np.array([[1, 0], [0, 0]]))
                full_operator_part_01 = kron(full_operator_part_01, np.array([[0, 0], [0, 1]]))
                full_operator_part_11 = kron(full_operator_part_11, np.array([[0, 0], [0, 1]]))
            elif i == idx3:
                full_operator_part_00 = kron(full_operator_part_00, OPERATOR_PAULI_I)
                full_operator_part_01 = kron(full_operator_part_01, OPERATOR_PAULI_I)
                full_operator_part_10 = kron(full_operator_part_10, OPERATOR_PAULI_I)
                full_operator_part_11 = kron(full_operator_part_11, operator)
            else:
                full_operator_part_00 = kron(full_operator_part_00, OPERATOR_PAULI_I)
                full_operator_part_01 = kron(full_operator_part_01, OPERATOR_PAULI_I)
                full_operator_part_10 = kron(full_operator_part_10, OPERATOR_PAULI_I)
                full_operator_part_11 = kron(full_operator_part_11, OPERATOR_PAULI_I)
        full_operator = full_operator_part_00 + full_operator_part_01 + full_operator_part_10 + full_operator_part_11
        qubit1.state.operate(full_operator)


Toffoli = ThreeQubitsGate(name="Toffoli Gate",
                          operator=OPERATOR_PAULI_X, _docs="The controlled-controlled (Toffoli) gate")
