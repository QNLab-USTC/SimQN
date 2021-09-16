from qns.models.qubit import Qubit, QState, H, CNOT, joint, swap, QUBIT_STATE_0, QUBIT_STATE_P
import numpy as np

q1 = Qubit(state=QUBIT_STATE_0, name="q1")
q2 = Qubit(state=QUBIT_STATE_0, name="q2")
q3 = Qubit(state=QUBIT_STATE_P, name="q3")
# CNOT(q1, q2)
# joint(q1, q3)
print(q1.measureY())
print(q1.measureY())


# nq = QState(qubits = [q1, q2, q3], state = np.matrix([1, 2, 3, 4, 5, 6, 7, 8]).H)
# q1.state = nq
# q2.state = nq
# q3.state = nq

# x1 = np.kron(OPERATOR_PAULI_I, OPERATOR_PAULI_X)
# x1 = np.kron(OPERATOR_PAULI_I, x1)

# print(x1)

# q1.state.operate(operator = x1)
# print(q1.state)
# q1.operate(OPERATOR_HADAMARD)
# print(q1.state)
# q1.state.operate(operator=OPERATOR_CNOT)
# print(q1.state)
# # q1.operate(OPERATOR_PAULI_Z)
# # print(q1.state)

# # q2.operate(OPERATOR_PAULI_Z)
# # print(q1.state)

# t1 = np.kron(OPERATOR_PAULI_Z, OPERATOR_PAULI_I)
# print(t1)

# e_vals,e_vecs = np.linalg.eig(t1)
# print(e_vals, e_vecs)
# A = np.matrix(e_vecs)
# print(np.dot(A.I, q1.state.state))

# print(np.dot(t1, q1.state.state))