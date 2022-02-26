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

from qns.models.qubit.const import QUBIT_STATE_0, QUBIT_STATE_1,\
        QUBIT_STATE_P, QUBIT_STATE_N, QUBIT_STATE_L, QUBIT_STATE_R
from qns.models.core.backend import QuantumModel
from qns.models.qubit.errors import QStateBaseError, QStateQubitNotInStateError,\
                                    QStateSizeNotMatchError, OperatorNotMatchError
from qns.utils.random import get_rand


def partial_trace(rho: np.ndarray, idx: int) -> np.ndarray:
    """
    Calculate the partial trace

    Args:
        rho: the density matrix
        idx (int): the index of removing qubit

    Returns:
        rho_res: the left density matric
    """

    num_qubit = int(np.log2(rho.shape[0]))
    qubit_axis = [(idx, num_qubit + idx)]
    minus_factor = [(i, 2 * i) for i in range(len(qubit_axis))]
    minus_qubit_axis = [(q[0] - m[0], q[1] - m[1])
                        for q, m in zip(qubit_axis, minus_factor)]
    rho_res = np.reshape(rho, [2, 2] * num_qubit)
    qubit_left = num_qubit - len(qubit_axis)
    for i, j in minus_qubit_axis:
        rho_res = np.trace(rho_res, axis1=i, axis2=j)
    if qubit_left > 1:
        rho_res = np.reshape(rho_res, [2 ** qubit_left] * 2)
    return rho_res


class QState(object):
    """
    QState is the state of one (or multiple) qubits
    """
    def __init__(self, qubits: List["Qubit"] = [], state: Optional[np.ndarray] = QUBIT_STATE_0,
                 rho: Optional[np.ndarray] = None, name: Optional[str] = None):
        """
        Args:
            qubits (List[Qubit]): a list of qubits in this quantum state
            state: the state vector of this state, either ``state`` or ``rho`` can be used to present a state
            rho: the density matrix of this state, either ``state`` or ``rho`` can be used to present a state
            name (str): the name of this state
        """
        self.num = len(qubits)
        self.name = name
        self.qubits = qubits
        self.rho = None

        if rho is None:
            if len(state) != 2**self.num:
                raise QStateSizeNotMatchError
            self.rho = np.dot(state, state.T.conjugate())
        else:
            if self.num != np.log2(rho.shape[0]) or self.num != np.log2(rho.shape[1]):
                raise QStateSizeNotMatchError
            if abs(1 - rho.trace()) > 0.0000000001:
                # trace = 1
                print(2333, 1 - rho.trace())
                raise QStateSizeNotMatchError
            self.rho = rho

    def measure(self, qubit: "Qubit" = None, base: str = "Z") -> int:
        """
        Measure this qubit using Z basis
        Args:
            qubit (Qubit): the measuring qubit
            base: the measure base, "Z", "X" or "Y"

        Returns:
            0: QUBIT_STATE_0 state
            1: QUBIT_STATE_1 state
        """
        M_0 = None
        M_1 = None
        S_0 = None
        S_1 = None
        if base == "Z":
            M_0 = np.array([[1, 0], [0, 0]])
            M_1 = np.array([[0, 0], [0, 1]])
            S_0 = QUBIT_STATE_0
            S_1 = QUBIT_STATE_1
        elif base == "X":
            M_0 = 1/2 * np.array([[1, 1], [1, 1]])
            M_1 = 1/2 * np.array([[1, -1], [-1, 1]])
            S_0 = QUBIT_STATE_P
            S_1 = QUBIT_STATE_N
        elif base == "Y":
            M_0 = 1/2 * np.array([[1, -1j], [1j, 1]])
            M_1 = 1/2 * np.array([[1, 1j], [-1j, 1]])
            S_0 = QUBIT_STATE_R
            S_1 = QUBIT_STATE_L
        else:
            raise QStateBaseError

        try:
            idx = self.qubits.index(qubit)
            shift = self.num - idx - 1
            assert(shift >= 0)
        except AssertionError:
            raise QStateQubitNotInStateError

        Full_M_0 = np.array([[1]])
        Full_M_1 = np.array([[1]])
        for i in range(self.num):
            if i == idx:
                Full_M_0 = np.kron(Full_M_0, M_0)
                Full_M_1 = np.kron(Full_M_1, M_1)
            else:
                Full_M_0 = np.kron(Full_M_0, np.array([[1, 0], [0, 1]]))
                Full_M_1 = np.kron(Full_M_1, np.array([[1, 0], [0, 1]]))

        poss_0 = np.trace(np.dot(Full_M_0.T.conjugate(), np.dot(Full_M_0, self.rho)))
        rn = get_rand()

        if rn < poss_0:
            ret = 0
            ret_s = S_0
            self.rho = np.dot(Full_M_0, np.dot(self.rho, Full_M_0.T.conjugate())) / poss_0
        else:
            ret = 1
            ret_s = S_1
            self.rho = np.dot(Full_M_1, np.dot(self.rho, Full_M_1.T.conjugate())) / (1-poss_0)

        self.rho = partial_trace(self.rho, idx)
        self.num -= 1
        self.qubits.remove(qubit)

        ns = QState([qubit], state=ret_s)
        qubit.state = ns
        return ret

    def operate(self, operator: np.ndarray):
        """
        transform using `operator`

        Args:
            operator (np.ndarray): the operator
        Raises:
            OperatorNotMatchError
        """
        operator_size = operator.shape
        if operator_size == (2**self.num, 2**self.num):
            # joint qubit operate
            full_operator = operator
        else:
            raise OperatorNotMatchError
        self.rho = np.dot(full_operator, np.dot(self.rho, full_operator.T.conjugate()))

    def equal(self, other_state: "QState") -> bool:
        """
        compare two state vectors, return True if they are the same

        Args:
            other_state (QState): the second QState
        """
        return np.all(self.rho == other_state.rho)

    def is_pure_state(self, eps: float = 0.000_001) -> bool:
        """
        Args:
            eps: the accuracy

        Returns:
            bool, if the state is a pure state
        """
        return abs(np.trace(np.dot(self.rho, self.rho)) - 1) <= eps

    def state(self) -> np.ndarray:
        """
        If the state is a pure state, return the state vector, or return None

        Returns:
            The pure state vector
        """
        if not self.is_pure_state():
            print(self.rho.T.conjugate() * self.rho)
            return None
        evs = np.linalg.eig(self.rho)
        max_idx = 0
        for idx, i in enumerate(evs[0]):
            if i > evs[0][max_idx]:
                max_idx = idx
        return evs[1][:, max_idx].reshape((2**self.num, 1))

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<qubit {self.name}: {self.rho}>"
        return str(self.rho)


class Qubit(QuantumModel):
    """
    Represent a qubit
    """

    def __init__(self, state=QUBIT_STATE_0, rho: np.ndarray = None, name: Optional[str] = None):
        """
        Args:
            state (list): the initial state of a qubit, default is |0> = [1, 0]^T
            name (str): the qubit's name
        """

        self.name = name
        self.state = QState([self], state=state, rho=rho)

    def measure(self):
        """
        Measure this qubit using Z basis

        Returns:
            0: QUBIT_STATE_0 state
            1: QUBIT_STATE_1 state
        """
        return self.state.measure(self)

    def measureX(self):
        """
        Measure this qubit using X basis.
        Only for not entangled qubits.

        Returns:
            0: QUBIT_STATE_P state
            1: QUBIT_STATE_N state
        """
        return self.state.measure(self, "X")

    def measureY(self):
        """
        Measure this qubit using Y basis.
        Only for not entangled qubits.

        Returns:
            0: QUBIT_STATE_R state
            1: QUBIT_STATE_L state
        """
        return self.state.measure(self, "Y")

    def measureZ(self):
        """
        Measure this qubit using Z basis

        Returns:
            0: QUBIT_STATE_0 state
            1: QUBIT_STATE_1 state
        """
        return self.measure()

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<Qubit {self.name}>"
        return super().__repr__()

    def storage_error_model(self, t: float, **kwargs):
        """
        The default error model for storing a qubit in quantum memory.
        The default behavior is doing nothing

        Args:
            t: the time stored in a quantum memory. The unit it second.
            kwargs: other parameters
        """
        pass

    def transfer_error_model(self, length: float, **kwargs):
        """
        The default error model for transmitting this qubit
        The default behavior is doing nothing

        Args:
            length (float): the length of the channel
            kwargs: other parameters
        """
        pass
