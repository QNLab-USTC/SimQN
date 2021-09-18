from qns.models.qubit import Qubit, QState, H, CNOT, X, Z, joint, swap, QUBIT_STATE_0, QUBIT_STATE_P
import numpy as np

q0 = Qubit(state=QUBIT_STATE_0, name="q0")
q1 = Qubit(state=QUBIT_STATE_0, name="q1")

H(q0)
CNOT(q0, q1)

print(q0.measure(), q1.measure())
