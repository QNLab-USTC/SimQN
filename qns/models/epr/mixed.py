#    SimQN: a discrete-event simulator for the quantum networks
#    Copyright (C) 2021-2022 Lutong Chen, Jian Li, Kaiping Xue
#    University of Science and Technology of China, USTC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import List, Optional
from qns.models.core.backend import QuantumModel
from qns.models.epr.entanglement import BaseEntanglement
from qns.models.qubit.const import QUBIT_STATE_0, QUBIT_STATE_P
from qns.models.qubit.qubit import QState, Qubit
import numpy as np

from qns.utils.random import get_rand


class MixedStateEntanglement(BaseEntanglement, QuantumModel):
    """
    `MixedStateEntanglement` is a pair of entangled qubits in mixed State with a hidden-variable.
    rho = A * Phi^+ + B * Psi^+ + C * Psi^- + D * Phi^-
    """
    def __init__(self, fidelity: float = 1, b: Optional[float] = None,
                 c: Optional[float] = None, d: Optional[float] = None,
                 name: Optional[str] = None):
        """
        generate an entanglement with certain fidelity

        Args:
            fidelity (float): the fidelity, equals to the probability of Phi^+
            b (float): probability of Psi^+
            c (float): probability of Psi^-
            d (float): probability of Phi^-
            name (str): the entanglement name
        """
        self.fidelity = fidelity
        self.b = b if b is not None else (1-fidelity)/3
        self.c = c if c is not None else (1-fidelity)/3
        self.d = d if d is not None else (1-fidelity)/3
        self.normalized()
        self.name = name
        self.is_decoherenced = False

    @property
    def a(self) -> float:
        """
        a equals to the fidelity
        """
        return self.fidelity

    @a.setter
    def a(self, fidelity: float = 1):
        self.fidelity = fidelity

    def normalized(self):
        total = self.a + self.b + self.c + self.d
        # Normalized: a + b + c + d = 1
        self.a = self.a/total
        self.b = self.b/total
        self.c = self.c/total
        self.d = self.d/total

    def swapping(self, epr: "MixedStateEntanglement", name: Optional[str] = None):
        """
        Use `self` and `epr` to perfrom swapping and distribute a new entanglement

        Args:
            epr (MixedEntanglement): another entanglement
            name (str): the name of the new entanglement
        Returns:
            the new distributed entanglement
        """
        ne = MixedStateEntanglement(name=name)
        if self.is_decoherenced or epr.is_decoherenced:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True

        ne.a = self.a*epr.a + self.b*epr.b + self.c*epr.c + self.d*epr.d
        ne.b = self.a*epr.b + self.b*epr.a + self.c*epr.d + self.d*epr.c
        ne.c = self.a*epr.c + self.b*epr.d + self.c*epr.a + self.d*epr.b
        ne.d = self.a*epr.d + self.b*epr.c + self.c*epr.d + self.d*epr.a
        ne.normalized()
        return ne

    def distillation(self, epr: "MixedStateEntanglement", name: Optional[str] = None):
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement.
        Using BBPSSW protocol.

        Args:
            epr (BaseEntanglement): another entanglement
            name (str): the name of the new entanglement
        Returns:
            the new distributed entanglement
        """
        ne = MixedStateEntanglement()
        if self.is_decoherenced or epr.is_decoherenced:
            ne.is_decoherenced = True
            ne.fidelity = 0
            return
        epr.is_decoherenced = True
        self.is_decoherenced = True
        p_succ = (self.a+self.d)*(epr.a+epr.d) + (self.b+self.c)*(epr.c + epr.b)

        if get_rand() > p_succ:
            ne.is_decoherenced = True
            ne.fidelity = 0
            return
        ne.a = (self.a*epr.a+self.d*epr.d)/p_succ
        ne.b = (self.b*epr.b+self.c*epr.c)/p_succ
        ne.c = (self.b*epr.c+self.c*epr.b)/p_succ
        ne.d = (self.a*epr.d+self.d*epr.a)/p_succ
        ne.normalized()
        return ne

    def storage_error_model(self, t: float, **kwargs):
        """
        The default error model for storing this entangled pair in a quantum memory.
        The default behavior is: a = 0.25 + (a-0.25)*e^{a*t}, default a = 0

        Args:
            t: the time stored in a quantum memory. The unit it second.
            kwargs: other parameters
        """
        a = kwargs.get("a", 0)
        self.a = 0.25 + (self.a-0.25) * np.exp(-a * t)
        self.b = 0.25 + (self.b-0.25) * np.exp(-a * t)
        self.c = 0.25 + (self.c-0.25) * np.exp(-a * t)
        self.d = 0.25 + (self.d-0.25) * np.exp(-a * t)
        self.normalized()

    def transfer_error_model(self, length: float, **kwargs):
        """
        The default error model for transmitting this entanglement.
        The success possibility of transmitting is: 0.25 + (a-0.25)*e^{b*l}, default b = 0

        Args:
            length (float): the length of the channel
            kwargs: other parameters
        """
        b = kwargs.get("b", 0)
        self.a = 0.25 + (self.a-0.25) * np.exp(-b * length)
        self.b = 0.25 + (self.b-0.25) * np.exp(-b * length)
        self.c = 0.25 + (self.c-0.25) * np.exp(-b * length)
        self.d = 0.25 + (self.d-0.25) * np.exp(-b * length)
        self.normalized()

    def to_qubits(self) -> List[Qubit]:
        if self.is_decoherenced:
            q0 = Qubit(state=QUBIT_STATE_P, name="q0")
            q1 = Qubit(state=QUBIT_STATE_P, name="q1")
            return [q0, q1]

        q0 = Qubit(state=QUBIT_STATE_0, name="q0")
        q1 = Qubit(state=QUBIT_STATE_0, name="q1")

        phi_p = 1/np.sqrt(2) * np.array([[1], [0], [0], [1]])
        phi_n = 1/np.sqrt(2) * np.array([[1], [0], [0], [-1]])
        psi_p = 1/np.sqrt(2) * np.array([[0], [1], [1], [0]])
        psi_n = 1/np.sqrt(2) * np.array([[0], [1], [-1], [0]])
        rho = self.a * np.dot(phi_p, phi_p.T.conjugate()) + self.b * np.dot(psi_p, psi_p.T.conjugate())\
            + self.c * np.dot(psi_n, psi_n.T.conjugate()) + self.d * np.dot(phi_n, phi_n.T.conjugate())

        qs = QState([q0, q1], rho=rho)
        q0.state = qs
        q1.state = qs
        self.is_decoherenced = True
        return [q0, q1]
