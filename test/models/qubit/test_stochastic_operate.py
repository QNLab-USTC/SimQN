from qns.models.qubit.qubit import Qubit
from qns.models.qubit.const import QUBIT_STATE_0, OPERATOR_PAULI_X, OPERATOR_PAULI_I
from qns.models.qubit import H, CNOT


def test_stochastic_operate():
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")
    H(q0)
    CNOT(q0, q1)

    q0.stochastic_operate([OPERATOR_PAULI_I, OPERATOR_PAULI_X], [0.5, 0.5])
    print(q0.state.rho)
