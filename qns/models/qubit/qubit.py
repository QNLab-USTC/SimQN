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
        self.state: np.ndarray = np.array(state)

    def measure(self, qubit: "Qubit" = None) -> int:
        try:
            idx = self.qubits.index(qubit)
            shift = self.num - idx - 1
            assert(shift >= 0)
        except:
            raise QStateQubitNotInStateError
        
        set_0, set_1 = [], []
        poss_0, poss_1 = 0, 0
        for l in range(2**self.num):
            if (l & (1<<shift)) > 0:
                set_1.append(l)
            else:
                set_0.append(l)

        ns = self.state.copy()
        for i in set_0:
            poss_0 += np.abs(ns[i][0])**2

        rn = np.random.rand()

        nns = []
        if rn <= poss_0:
            ret = 0
            ret_s = QUBIT_STATE_0
            for i in set_0:
                nns.append(ns[i])
        else:
            ret = 1
            ret_s = QUBIT_STATE_1
            for i in set_1:
                nns.append(ns[i])

        ns1 = QState([qubit], ret_s)
        qubit.state = ns1
        self.num -= 1
        self.qubits.remove(qubit)
        self.state = np.array(nns)
        self._to_1()
        return ret

    def _to_1(self):
        poss = 0
        for i in range(2**self.num):
            poss += np.abs(self.state[i][0])**2
        amp = np.sqrt(1 / poss)
        for i in range(2**self.num):
            self.state[i][0] = amp * self.state[i][0]

    def operate(self, operator: np.ndarray = None):
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

    def measure(self):
        return self.state.measure(self)

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<Qubit {self.name}>"
        return super().__repr__()