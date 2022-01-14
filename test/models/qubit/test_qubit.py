from qns.models.qubit.qubit import Qubit
from qns.models.qubit.gate import H, CNOT, RX, RY, RZ, U, CZ, CR, Swap, Toffoli
from qns.models.qubit.const import QUBIT_STATE_0, QUBIT_STATE_1, OPERATOR_RX, OPERATOR_RZ, OPERATOR_RY
import numpy as np


def test_qubit():
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")

    H(q0)
    CNOT(q0, q1)

    assert(q0.measure() == q1.measure())


def test_qubit_rotate():
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")
    RX(q0)
    U(q1, OPERATOR_RX(theta=np.pi/4))
    assert(q0.state.equal(q1.state))

    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")
    RY(q0)
    U(q1, OPERATOR_RY(theta=np.pi/4))
    assert(q0.state.equal(q1.state))

    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")
    RZ(q0)
    U(q1, OPERATOR_RZ(theta=np.pi/4))
    assert(q0.state.equal(q1.state))


def test_2qubit():
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")
    H(q0)
    CZ(q0, q1)

    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_0, name="q1")
    H(q0)
    CR(q0, q1, theta=np.pi/4)


def test_swap():
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q1 = Qubit(state=QUBIT_STATE_1, name="q1")
    q2 = Qubit(state=QUBIT_STATE_0, name="q2")

    Swap(q0, q1)
    Swap(q0, q2)

    assert(q0.measure() == q1.measure())
    assert(q2.measure() == 1)


def test_toffoli():
    a = [QUBIT_STATE_0, QUBIT_STATE_1]
    import itertools
    all = itertools.product(a, a)
    for c in all:
        q0 = Qubit(state=c[0], name="q0")
        q1 = Qubit(state=c[1], name="q1")
        q2 = Qubit(state=QUBIT_STATE_0, name="q2")
        Toffoli(q0, q1, q2)
        c2 = q2.measure()
        if (c[0] == QUBIT_STATE_1).all() and (c[1] == QUBIT_STATE_1).all():
            assert(c2 == 1)
        else:
            assert(c2 == 0)
