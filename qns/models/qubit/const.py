import numpy as np

QUBIT_STATE_0 = np.array([[1], [0]], dtype=np.complex128)
QUBIT_STATE_1 = np.array([[0], [1]], dtype=np.complex128)

QUBIT_STATE_P = 1 / np.sqrt(2) * np.array([[1], [1]], dtype=np.complex128)
QUBIT_STATE_N = 1 / np.sqrt(2) * np.array([[1], [-1]], dtype=np.complex128)

QUBIT_STATE_R = 1 / np.sqrt(2) * np.array([[-1j], [1]], dtype=np.complex128)
QUBIT_STATE_L = 1 / np.sqrt(2) * np.array([[1], [-1j]], dtype=np.complex128)

OPERATOR_HADAMARD = 1 / np.sqrt(2) * np.array([[1, 1], [1, -1]], dtype=np.complex128)
OPERATOR_T = np.array([[1, 0], [0, np.e**(1j * np.pi / 4)]], dtype=np.complex128)
OPERATOR_S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)

OPERATOR_PAULI_I = np.array([[1, 0], [0, 1]], dtype=np.complex128)
OPERATOR_PAULI_X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
OPERATOR_PAULI_Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
OPERATOR_PAULI_Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)


def OPERATOR_PHASE_SHIFT(theta: float):
    return np.array([[1, 0], [0, np.e**(1j * theta)]], dtype=np.complex128)


OPERATOR_CNOT = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
                         dtype=np.complex128)
OPERATOR_SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]],
                         dtype=np.complex128)

BASIS_Z = OPERATOR_PAULI_Z
BASIS_X = OPERATOR_PAULI_X
BASIS_Y = OPERATOR_PAULI_Y
