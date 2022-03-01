from qns.models.qubit.qubit import Qubit
from qns.models.qubit.const import QUBIT_STATE_0, OPERATOR_PAULI_X, OPERATOR_PAULI_I
from qns.models.qubit import H, CNOT, I, X, Y, Z


def test_stochastic_operate():
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")
    H(q0)
    CNOT(q0, q1)

    q0.stochastic_operate([OPERATOR_PAULI_I, OPERATOR_PAULI_X], [0.5, 0.5])


def test_stochastic_operate2():

    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q0.operate(Y)
    print(q0.state)

    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q0.stochastic_operate([I, X, Y, Z], [0.7, 0.1, 0.1, 0.1])
