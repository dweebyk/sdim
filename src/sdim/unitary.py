import numpy as np
import cirq
from itertools import product

def generate_tau(d):
    return np.exp(1j * np.pi * (d**2 + 1) / d)

def generate_identity_matrix(d):
    return np.eye(d)

def generate_x_matrix(d):
    X = np.zeros((d, d), dtype=np.complex128)
    for i in range(d):
        X[i, (i - 1) % d] = 1
    return X

def generate_z_matrix(d):
    Z = np.zeros((d, d), dtype=np.complex128)
    for i in range(d):
        Z[i, i] = np.exp(2 * np.pi * 1j * i / d)
    return Z

def generate_h_matrix(d):
    H = np.zeros((d, d), dtype=np.complex128)
    tau = generate_tau(d)
    for m in range(d):
        for n in range(d):
            H[m, n] = 1 / np.sqrt(d) * tau**(2 * m * n)
    return H

def generate_m_matrix(d, a):
    M = np.zeros((d, d), dtype=np.complex128)
    if np.gcd(a, d) != 1:
        raise ValueError("a and d must be coprime")
    for q in range(d):
        M[a*q % d, q] = 1
    return M

def generate_p_matrix(d):
    P = np.eye(d, dtype=np.complex128)
    tau = generate_tau(d)
    for j in range(d):
        P[j, j] = tau ** (j ** 2)
    return P

def generate_cnot_matrix(d):
    omega = np.exp(2j * np.pi / d)
    CNOT = np.zeros((d**2, d**2),dtype=np.complex128)
    for i, j in product(range(d), repeat=2):
        # phase = omega**((i + j) / 2) if d % 2 == 0 else 1
        phase = 1
        CNOT[d * i + j, d * i + (i + j) % d] = phase
    CNOT = CNOT.reshape(d**2, d**2)
    CNOT = CNOT.transpose()
    return CNOT


class GeneralizedHadamardGate(cirq.Gate):
    def __init__(self, d):
        super(GeneralizedHadamardGate, self).__init__()
        self.d = d

    def _qid_shape_(self):
        return (self.d,)

    def _unitary_(self):
        return generate_h_matrix(self.d)

    def _circuit_diagram_info_(self, args):
        return f"H_{self.d}"


class GeneralizedPhaseShiftGate(cirq.Gate):
    def __init__(self, d):
        super(GeneralizedPhaseShiftGate, self).__init__()
        self.d = d

    def _qid_shape_(self):
        return (self.d,)

    def _unitary_(self):
        return generate_p_matrix(self.d)

    def _circuit_diagram_info_(self, args):
        return f"P_{self.d}"

class GeneralizedXPauliGate(cirq.Gate):
    def __init__(self, d):
        super(GeneralizedXPauliGate, self).__init__()
        self.d = d

    def _qid_shape_(self):
        return (self.d,)

    def _unitary_(self):
        return generate_x_matrix(self.d)

    def _circuit_diagram_info_(self, args):
        return f"X_{self.d}"
    
class GeneralizedZPauliGate(cirq.Gate):
    def __init__(self, d):
        super(GeneralizedZPauliGate, self).__init__()
        self.d = d

    def _qid_shape_(self):
        return (self.d,)

    def _unitary_(self):
        return generate_z_matrix(self.d)

    def _circuit_diagram_info_(self, args):
        return f"Z_{self.d}"
    
class GeneralizedCNOTGate(cirq.Gate):
    def __init__(self, d):
        super(GeneralizedCNOTGate, self).__init__()
        self.d = d

    def _qid_shape_(self):
        return (self.d, self.d)

    def _unitary_(self):
        return generate_cnot_matrix(self.d)

    def _circuit_diagram_info_(self, args):
        return (f"CNOT_{self.d}_control", f"CNOT_{self.d}_target")
    
class IdentityGate(cirq.Gate):
    def __init__(self, d):
        super(IdentityGate, self).__init__()
        self.d = d

    def _qid_shape_(self):
        return (self.d,)

    def _unitary_(self):
        return generate_identity_matrix(self.d)

    def _circuit_diagram_info_(self, args):
        return f"I_{self.d}"