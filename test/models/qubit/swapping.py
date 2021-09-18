from qns.models.qubit import Qubit, QState, H, CNOT, X, Z, joint, swap, QUBIT_STATE_0, QUBIT_STATE_P
import numpy as np

q0 = Qubit(state=QUBIT_STATE_0, name="q0")
q1 = Qubit(state=QUBIT_STATE_0, name="q1")
q2 = Qubit(state=QUBIT_STATE_0, name="q2")
q3 = Qubit(state=QUBIT_STATE_0, name="q3")


H(q0)
CNOT(q0, q1)
H(q2)
CNOT(q2, q3)
CNOT(q1, q2)
H(q1)

c0 = q2.measure()
c1 = q1.measure()
print(c0, c1)

if c0==1 and c1 == 0:
    X(q3)
elif c0 == 0 and c1 == 1:
    Z(q3)
elif c0 == 1 and c1 == 1:
    X(q3)
    Z(q3)

print(q0.state)
