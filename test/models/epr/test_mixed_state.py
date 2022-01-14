from qns.models.epr import MixedStateEntanglement
from qns.models.qubit.const import QUBIT_STATE_0
from qns.models.qubit.qubit import Qubit


def test_mixed_state():

    e1 = MixedStateEntanglement(fidelity=0.95, name="e1")
    e2 = MixedStateEntanglement(fidelity=0.95, name="e2")
    e3 = e1.swapping(e2)
    print(e3.fidelity)

    e4 = MixedStateEntanglement(fidelity=0.95, name="e4")
    e5 = MixedStateEntanglement(fidelity=0.95, name="e5")
    e6 = e4.swapping(e5)
    print(e6.fidelity)

    e7 = e3.distillation(e6)
    if e7 is None:
        print("distillation failed")
        return
    print(e7.fidelity)

    e8 = MixedStateEntanglement(fidelity=0.95, name="e8")
    e9 = e7.distillation(e8)
    if e9 is None:
        print("distillation failed")
        return
    print(e9.fidelity, e9.b, e9.c, e9.d)

    q_in = Qubit(QUBIT_STATE_0)
    q_out = e9.teleportion(q_in)
    print(q_out.state.rho)


if __name__ == "__main__":
    test_mixed_state()
