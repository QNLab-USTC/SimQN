from qns.models.qubit.qubit import Qubit
from qns.models.qubit.gate import H, CNOT
from qns.models.qubit.const import QUBIT_STATE_0


def test_qubit():
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")

    H(q0)
    CNOT(q0, q1)

    assert(q0.measure() == q1.measure())
