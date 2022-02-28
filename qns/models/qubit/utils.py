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


class OperatorError(Exception):
    pass


def single_gate_expand(qubit: "Qubit", operator: np.ndarray) -> np.ndarray:
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
            full_operator = np.kron(full_operator, operator)
        else:
            full_operator = np.kron(full_operator, OPERATOR_PAULI_I)
    return full_operator
