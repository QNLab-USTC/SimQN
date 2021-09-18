from qns.models.epr import BellStateEntanglement, WernerStateEntanglement
from qns.models.qubit import QUBIT_STATE_0, Qubit

e1 = BellStateEntanglement(fidelity= 0.8, name="e1")
q0, q1 = e1.to_qubits()
print(q1.state)


c0 = 0
c1 = 0
for i in range(1000):
    q0 = Qubit( QUBIT_STATE_0)
    e1 = BellStateEntanglement(fidelity= 0.8, name="e0")
    q2 = e1.teleportion(q0)
    if q2.measure() == 0:
        c0 += 1
    else:
        c1 += 1
print(c0, c1)