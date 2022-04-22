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
from qns.models.qubit.const import OPERATOR_PAULI_I
from qns.models.qubit.errors import QGateStateJointError, OperatorError


def kron(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    x = a.shape
    y = b.shape
    if a.shape == (1,):
        a = a.reshape((1, 1))
    if b.shape == (1,):
        b = b.reshape((1, 1))
    print(a, b)
    return (a[:, None, :, None]*b[None, :, None, :]).reshape(a.shape[0]*b.shape[0], a.shape[1]*b.shape[1])


def single_gate_expand(qubit, operator: np.ndarray) -> np.ndarray:
    state = qubit.state
    if operator.shape != (2, 2):
        raise OperatorError

    # single qubit operate
    try:
        idx = state.qubits.index(qubit)
    except ValueError:
        raise OperatorError
    full_operator = np.array([1])
    for i in range(state.num):
        if i == idx:
            full_operator = kron(full_operator, operator)
        else:
            full_operator = kron(full_operator, OPERATOR_PAULI_I)
    return full_operator


def joint(qubit1, qubit2) -> None:
    if qubit1.state == qubit2.state:
        return
    if len(set(qubit1.state.qubits) & set(qubit2.state.qubits)) > 0:
        raise QGateStateJointError

    from qns.models.qubit.qubit import QState
    nq = QState(qubit1.state.qubits+qubit2.state.qubits,
                rho=kron(qubit1.state.rho, qubit2.state.rho))
    for q in nq.qubits:
        q.state = nq


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
