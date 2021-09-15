from typing import List, Optional
import numpy as np
from numpy.core.numeric import full
from .const import *

class QStateSizeNotMatchError(Exception):
    """
    This error happens when the size of state vector or matrix mismatch occurs
    """
    pass

class QStateQubitNotInStateError(Exception):
    pass

class OperatorNotMatchError(Exception):
    """
    This error happens when the size of state vector or matrix mismatch occurs
    """
    pass


class QState():
    """
    QState is the state of one (or multiple) qubits
    """
    def __init__(self, qubits: List["Qubit"] = [] ,state: Optional[List[complex]] = QUBIT_STATE_0):
        self.num = len(qubits)

        if len(state) != 2**self.num:
            raise QStateSizeNotMatchError
        self.qubits = qubits
        self.state = np.array(state)

    def measure(self, qubit: "Qubit" = None, basis = None):
        pass

    def operate(self, qubit: "Qubit" = None, operator: np.ndarray = None):
        operator_size = operator.shape
        if qubit is not None and operator_size == (2, 2):           
            # single qubit operate
            try:
                idx = self.qubits.index(qubit)
            except:
                raise QStateQubitNotInStateError
            full_operator = np.array([1])
            for i in range(self.num):
                if i == idx:
                    full_operator = np.kron(full_operator, operator)
                else:
                    full_operator = np.kron(full_operator, OPERATOR_PAULI_I)

        elif operator_size == (2**self.num, 2**self.num):
            # joint qubit operate
            full_operator = operator
        else:
            raise OperatorNotMatchError
        self.state = np.dot(full_operator, self.state)

    def __repr__(self) -> str:
        return str(self.state)

class Qubit():
    """
    Represent a qubit
    """

    def __init__(self, state = QUBIT_STATE_0, name: Optional[str] = None):
        """ 
        Args:
            state (list): the initial state of a qubit, default is |0> = [1, 0]^T
            name (str): the qubit's name
        """

        self.name = name
        self.state = QState([self], state)

    def measure(self, basis = BASIS_Z):
        return self.state.measure(self, basis)

    def operate(self, operator):
        return self.state.operate(self, operator)

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<Qubit {self.name}>"
        return super().__repr__()