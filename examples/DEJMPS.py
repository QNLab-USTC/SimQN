from qns.models.epr.mixed import MixedStateEntanglement
from qns.models.qubit.gate import RX, CNOT
import numpy as np


def DEJMPS(q1, q2, q3, q4):
    """
    The BEJMPS distillation protocol
    """
    RX(q1, np.pi/2)
    RX(q2, np.pi/2)
    RX(q3, -np.pi/2)
    RX(q4, -np.pi/2)

    CNOT(q1, q2)
    CNOT(q3, q4)
    c2 = q2.measure()
    c4 = q4.measure()
    if c2 == c4:
        return True, q1, q3
    return False, None, None


def main():
    fail_count = 0
    succ_count = 0
    fidelity = None
    for _ in range(1000):
        e1 = MixedStateEntanglement(fidelity=0.8)
        e2 = MixedStateEntanglement(fidelity=0.8)

        q1, q3 = e1.to_qubits()
        print(q1.state.state)
        q2, q4 = e2.to_qubits()

        ret, q1, q3 = DEJMPS(q1, q2, q3, q4)
        if ret:
            succ_count += 1
            rho = q1.state.rho
            phi_p: np.ndarray = 1/np.sqrt(2) * np.array([[1, 0, 0, 1]])
            fidelity = np.dot(phi_p, rho)
            fidelity = np.dot(fidelity, phi_p.T.conj())
        else:
            fail_count += 1
    print(succ_count, fail_count, rho, fidelity)


if __name__ == "__main__":
    main()
