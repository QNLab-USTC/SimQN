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

import numpy as np
from qns.models.qubit.const import OPERATOR_HADAMARD, OPERATOR_PAULI_I,\
                                   OPERATOR_PAULI_X, OPERATOR_PAULI_Y, \
                                   OPERATOR_PAULI_Z, OPERATOR_PHASE_SHIFT,\
                                   OPERATOR_RX, OPERATOR_RY, OPERATOR_RZ,\
                                   OPERATOR_S, OPERATOR_T
from qns.models.qubit.qubit import QState, Qubit


class QGateQubitNotInStateError(Exception):
    """
    This error happens when the qubit is not in the QState
    """
    pass


class QGateOperatorNotMatchError(Exception):
    """
    This error happens when the size of state vector or matrix mismatch occurs
    """
    pass


class QGateStateJointError(Exception):
    """
    This error happens when the size of state vector or matrix mismatch occurs
    """
    pass


def _single_gate_expand(qubit: Qubit, operator: np.ndarray) -> np.ndarray:
    state = qubit.state
    if operator.shape != (2, 2):
        raise QGateOperatorNotMatchError

    # single qubit operate
    try:
        idx = state.qubits.index(qubit)
    except ValueError:
        raise QGateQubitNotInStateError
    full_operator = np.array([1])
    for i in range(state.num):
        if i == idx:
            full_operator = np.kron(full_operator, operator)
        else:
            full_operator = np.kron(full_operator, OPERATOR_PAULI_I)
    return full_operator


def joint(qubit1: Qubit, qubit2: Qubit) -> None:
    if qubit1.state == qubit2.state:
        return
    if len(set(qubit1.state.qubits) & set(qubit2.state.qubits)) > 0:
        raise QGateStateJointError

    nq = QState(qubit1.state.qubits + qubit2.state.qubits,
                np.kron(qubit1.state.state, qubit2.state.state))
    for q in nq.qubits:
        q.state = nq
    return


def swap(qubit: Qubit, pos1: int, pos2: int) -> None:
    """
    Swap the state vector on pos1-th line and pos2-th line

    Args:
        qubit (Qubit): the swapping qubit
        pos1 (int): the first position
        pos2 (int): the second position
    """
    qubit.state.state[pos1][0], qubit.state.state[pos2][0]\
        = qubit.state.state[pos2][0], qubit.state.state[pos1][0]


def X(qubit: Qubit) -> None:
    """
    The pauli X gate

    Args:
        qubit (Qubit): the operating qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_PAULI_X)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def Y(qubit: Qubit) -> None:
    """
    The pauli Y gate

    Args:
        qubit (Qubit): the operating qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_PAULI_Y)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def Z(qubit: Qubit) -> None:
    """
    The pauli Z gate

    Args:
        qubit (Qubit): the operating qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_PAULI_Z)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def I(qubit: Qubit) -> None:
    """
    The pauli I gate (do nothing)

    Args:
        qubit (Qubit): the operating qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_PAULI_I)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def H(qubit: Qubit) -> None:
    """
    The Hadamard gate

    Args:
        qubit (Qubit): the operating qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_HADAMARD)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def T(qubit: Qubit) -> None:
    """
    The T gate (pi/4 shift gate)

    Args:
        qubit (Qubit): the operating qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_T)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def S(qubit: Qubit) -> None:
    """
    The S gate：

        [[1, 0]
        [0, j]]

    Args:
        qubit (Qubit): the operating qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_S)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def R(qubit: Qubit, theta: float = np.pi / 4) -> None:
    """
    The R gate (phase shift gate):

        [[1, 0]
        [0, theta * j]]

    Args:
        qubit (Qubit): the operating qubit
        theta (float): the rotation degree

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_PHASE_SHIFT(theta))
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def RX(qubit: Qubit, theta: float = np.pi / 4) -> None:
    """
    The Rx gate (X rotate gate):

        [[cos(theta/2), -j * sin(theta/2)],
        [-j * sin(theta/2), cos(theta/2)]]

    Args:
        qubit (Qubit): the operating qubit
        theta (float): the rotation degree

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_RX(theta))
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def RY(qubit: Qubit, theta: float = np.pi / 4) -> None:
    """
    The Ry gate (Y rotate gate):

        [[cos(theta/2), -sin(theta/2)],
        [sin(theta/2), cos(theta/2)]]

    Args:
        qubit (Qubit): the operating qubit
        theta (float): the rotation degree

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_RY(theta))
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def RZ(qubit: Qubit, theta: float = np.pi / 4) -> None:
    """
    The Rz gate (Z rotate gate):

        [[e^(-0.5j * theta), 0],
        [0, e^(0.5j * theta)]]

    Args:
        qubit (Qubit): the operating qubit
        theta (float): the rotation degree

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    full_operation = _single_gate_expand(qubit, OPERATOR_RZ(theta))
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def U(qubit: Qubit, operator: np.ndarray):
    """
    The arbitrary single qubit operation gate.

    Args:
        qubit (Qubit): the operating qubit
        operator (np.ndarray): a 2x2 operation matrix

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
    """
    if operator.shape != (2, 2):
        raise QGateOperatorNotMatchError
    full_operation = _single_gate_expand(qubit, operator)
    qubit.state.state = np.dot(full_operation, qubit.state.state)


def ControlledGate(qubit1: Qubit, qubit2: Qubit, operator: np.ndarray = OPERATOR_PAULI_X):
    """
    The controlled  gate:

        [[I_2, 0][0, operator]]

    Args:
        qubit1 (Qubit): the first qubit (controller)
        qubit2 (Qubit): the second qubit
        operator (np.ndarray): the gate on the second qubit if the first qubit is 1,
            default is pauli X (CNOT)

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
        QGateStateJointError
    """
    if qubit1 == qubit2:
        return
    joint(qubit1, qubit2)

    state = qubit1.state

    if operator.shape != (2, 2):
        raise QGateOperatorNotMatchError

    # single qubit operate
    try:
        idx1 = state.qubits.index(qubit1)
        idx2 = state.qubits.index(qubit2)
    except ValueError:
        raise QGateQubitNotInStateError

    full_operator_part_0 = np.array([1])  # |0> <0|
    full_operator_part_1 = np.array([1])  # |1> <1|

    for i in range(state.num):
        if i == idx1:
            full_operator_part_0 = np.kron(full_operator_part_0, np.array([[1, 0], [0, 0]]))
            full_operator_part_1 = np.kron(full_operator_part_1, np.array([[0, 0], [0, 1]]))
        elif i == idx2:
            full_operator_part_0 = np.kron(full_operator_part_0, OPERATOR_PAULI_I)
            full_operator_part_1 = np.kron(full_operator_part_1, operator)
        else:
            full_operator_part_0 = np.kron(full_operator_part_0, OPERATOR_PAULI_I)
            full_operator_part_1 = np.kron(full_operator_part_1, OPERATOR_PAULI_I)
    full_operator = full_operator_part_0 + full_operator_part_1
    state.state = np.dot(full_operator, state.state)
    return


def CNOT(qubit1: Qubit, qubit2: Qubit):
    """
    The controlled Pauli-X gate:

        [[I_2, 0][0, X]]

    Args:
        qubit1 (Qubit): the first qubit (controller)
        qubit2 (Qubit): the second qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
        QGateStateJointError
    """
    return ControlledGate(qubit1=qubit1, qubit2=qubit2)


def CZ(qubit1: Qubit, qubit2: Qubit):
    """
    The controlled Pauli-Z gate:

        [[I_2, 0][0, Z]]

    Args:
        qubit1 (Qubit): the first qubit (controller)
        qubit2 (Qubit): the second qubit

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
        QGateStateJointError
    """
    return ControlledGate(qubit1=qubit1, qubit2=qubit2, operator=OPERATOR_PAULI_Z)


def CR(qubit1: Qubit, qubit2: Qubit, theta: float = np.pi/4):
    """
    The controlled Rotate gate:

        [[I_2, 0][0, R(theta)]]

    Args:
        qubit1 (Qubit): the first qubit (controller)
        qubit2 (Qubit): the second qubit
        theta: the rotation degree

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
        QGateStateJointError
    """
    return ControlledGate(qubit1=qubit1, qubit2=qubit2, operator=OPERATOR_PHASE_SHIFT(theta))


def Swap(qubit1: Qubit, qubit2: Qubit):
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


def Toffoli(qubit1: Qubit, qubit2: Qubit, qubit3: Qubit, operator: np.ndarray = OPERATOR_PAULI_X):
    """
    The controlled-controlled (Toffoli) gate:

        [[I_6, 0][0, operator]]

    Args:
        qubit1 (Qubit): the first controll qubit
        qubit2 (Qubit): the second controll qubit
        qubit3 (Qubit): the operation qubit
        operator (np.ndarray): the gate on the third qubit if both the first and the second qubit is 1,
            default is pauli X (CNOT)

    Raises:
        QGateOperatorNotMatchError
        QGateQubitNotInStateError
        QGateStateJointError
    """
    if qubit1 == qubit2 or qubit1 == qubit3 or qubit2 == qubit3:
        return
    joint(qubit1, qubit2)
    joint(qubit2, qubit3)

    state = qubit1.state

    if operator.shape != (2, 2):
        raise QGateOperatorNotMatchError

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
            full_operator_part_00 = np.kron(full_operator_part_00, np.array([[1, 0], [0, 0]]))
            full_operator_part_01 = np.kron(full_operator_part_01, np.array([[1, 0], [0, 0]]))
            full_operator_part_10 = np.kron(full_operator_part_10, np.array([[0, 0], [0, 1]]))
            full_operator_part_11 = np.kron(full_operator_part_11, np.array([[0, 0], [0, 1]]))
        elif i == idx2:
            full_operator_part_00 = np.kron(full_operator_part_00, np.array([[1, 0], [0, 0]]))
            full_operator_part_10 = np.kron(full_operator_part_10, np.array([[1, 0], [0, 0]]))
            full_operator_part_01 = np.kron(full_operator_part_01, np.array([[0, 0], [0, 1]]))
            full_operator_part_11 = np.kron(full_operator_part_11, np.array([[0, 0], [0, 1]]))
        elif i == idx3:
            full_operator_part_00 = np.kron(full_operator_part_00, OPERATOR_PAULI_I)
            full_operator_part_01 = np.kron(full_operator_part_01, OPERATOR_PAULI_I)
            full_operator_part_10 = np.kron(full_operator_part_10, OPERATOR_PAULI_I)
            full_operator_part_11 = np.kron(full_operator_part_11, operator)
        else:
            full_operator_part_00 = np.kron(full_operator_part_00, OPERATOR_PAULI_I)
            full_operator_part_01 = np.kron(full_operator_part_01, OPERATOR_PAULI_I)
            full_operator_part_10 = np.kron(full_operator_part_10, OPERATOR_PAULI_I)
            full_operator_part_11 = np.kron(full_operator_part_11, OPERATOR_PAULI_I)
    full_operator = full_operator_part_00 + full_operator_part_01 + full_operator_part_10 + full_operator_part_11
    state.state = np.dot(full_operator, state.state)
