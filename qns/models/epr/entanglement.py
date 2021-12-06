from typing import List, Optional
import numpy as np
import random

from qns.models.core.backend import QuantumModel
from qns.models.qubit.qubit import Qubit, QState
from qns.models.qubit.gate import H, X, Y, Z, CNOT
from qns.models.qubit.const import QUBIT_STATE_0, QUBIT_STATE_P


class BaseEntanglement(object):
    """
    This is the base entanglement model
    """
    def __init__(self, fidelity: float = 1, name: Optional[str] = None):
        """
        generate an entanglement with certain fidelity

        Args:
            fidelity (float): the fidelity
            name (str): the entanglement name
        """
        self.fidelity = fidelity
        self.name = name
        self.is_decoherenced = False

    def swapping(self, epr: "BaseEntanglement") -> "BaseEntanglement":
        """
        Use `self` and `epr` to perfrom swapping and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entanglement
        """
        raise NotImplementedError

    def distillation(self, epr: "BaseEntanglement") -> "BaseEntanglement":
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entanglement
        """
        raise NotImplementedError

    def to_qubits(self) -> List[Qubit]:
        """
        Transport the entanglement into a pair of qubits based on the fidelity.
        Suppose the first qubit is [1/sqrt(2), 1/sqrt(2)].H

        Returns:
            A list of two qubits
        """
        if self.is_decoherenced:
            q0 = Qubit(state=QUBIT_STATE_P, name="q0")
            q1 = Qubit(state=QUBIT_STATE_P, name="q1")
            return [q0, q1]
        q0 = Qubit(state=QUBIT_STATE_0, name="q0")
        q1 = Qubit(state=QUBIT_STATE_0, name="q1")
        a = np.sqrt(self.fidelity/2)
        b = np.sqrt((1-self.fidelity)/2)
        qs = QState([q0, q1], state=np.array([[a], [b], [b], [a]]))
        q0.state = qs
        q1.state = qs
        return [q0, q1]

    def teleportion(self, qubit: Qubit) -> Qubit:
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entanglement
        """
        q1, q2 = self.to_qubits()
        CNOT(qubit, q1)
        H(qubit)
        c0 = qubit.measure()
        c1 = q1.measure()
        if c1 == 1 and c0 == 0:
            X(q2)
        elif c1 == 0 and c0 == 1:
            Z(q2)
        elif c1 == 1 and c0 == 1:
            Y(q2)
            q2.state.state = 1j * q2.state.state
        self.is_decoherenced = True
        return q2

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<entanglement {self.name}>"
        return super().__repr__()


class BellStateEntanglement(BaseEntanglement, QuantumModel):
    """
    `BellStateEntanglement` is the ideal max entangled qubits. Its fidelity is always 1.
    """

    def __init__(self, fidelity: float = 1, name: Optional[str] = None, p_swap: float = 1):
        super().__init__(fidelity=fidelity, name=name)
        self.p_swap = p_swap

    def swapping(self, epr: "BellStateEntanglement"):
        ne = BellStateEntanglement()
        if self.is_decoherenced or epr.is_decoherenced:
            ne.is_decoherenced = True
            ne.fidelity = 0

        r = random.random()
        if r > min(self.p_swap, epr.p_swap):
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        return ne

    def distillation(self, epr: "BellStateEntanglement"):
        ne = BellStateEntanglement()
        if self.is_decoherenced or epr.is_decoherenced:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        return ne

    def storage_error_model(self, t: float, **kwargs):
        """
        The default error model for storing this entangled pair in a quantum memory.
        The default behavior is doing nothing

        Args:
            t: the time stored in a quantum memory. The unit it second.
            kwargs: other parameters
        """
        pass

    def transfer_error_model(self, length: float, **kwargs):
        """
        The default error model for transmitting this entanglement.
        The default behavior is doing nothing

        Args:
            length (float): the length of the channel
            kwargs: other parameters
        """
        pass


class WernerStateEntanglement(BaseEntanglement, QuantumModel):
    """
    `WernerStateEntanglement` is a pair of entangled qubits in Werner State with a hidden-variable.
    """
    def __init__(self, fidelity: float = 1, name: Optional[str] = None):
        """
        generate an entanglement with certain fidelity

        Args:
            fidelity (float): the fidelity
            name (str): the entanglement name
        """
        self.w = (fidelity * 4 - 1)/3
        self.name = name
        self.is_decoherenced = False

    @property
    def fidelity(self) -> float:
        return (self.w * 3 + 1)/4

    @fidelity.setter
    def fidelity(self, fidelity: float = 1):
        self.w = (fidelity * 4 - 1)/3

    def swapping(self, epr: "WernerStateEntanglement", name: Optional[str] = None):
        """
        Use `self` and `epr` to perfrom swapping and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
            name (str): the name of the new entanglement
        Returns:
            the new distributed entanglement
        """
        ne = WernerStateEntanglement(name=name)
        if self.is_decoherenced or epr.is_decoherenced:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        ne.w = self.w * epr.w
        if self.fidelity <= 0.5:
            self.fidelity = 0.5
            self.is_decoherenced = True
        return ne

    def distillation(self, epr: "BellStateEntanglement", name: Optional[str] = None):
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement.
        Using Bennett 96 protocol and estimate lower bound.

        Args:
            epr (BaseEntanglement): another entanglement
            name (str): the name of the new entanglement
        Returns:
            the new distributed entanglement
        """
        ne = BellStateEntanglement()
        if self.is_decoherenced or epr.is_decoherenced:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        fmin = min(self.fidelity, epr.fidelity)
        ne.fidelity = (fmin**2 + (1-fmin)**2/9)/(fmin**2 + 5/9*(1-fmin)**2 + 2/3*fmin*(1-fmin))
        return ne

    def storage_error_model(self, t: float, **kwargs):
        """
        The default error model for storing this entangled pair in a quantum memory.
        The default behavior is: w = w*e^{-a*t}, default a = 0

        Args:
            t: the time stored in a quantum memory. The unit it second.
            kwargs: other parameters
        """
        a = kwargs.get("a", 0)
        self.w = self.w * np.exp(-a * t)

    def transfer_error_model(self, length: float, **kwargs):
        """
        The default error model for transmitting this entanglement.
        The success possibility of transmitting is: p = 10^{-b*D}, default b = 0

        Args:
            length (float): the length of the channel
            kwargs: other parameters
        """
        b = kwargs.get("b", 0)
        r = random.random()
        if r <= 10**(-b * length):
            return
        self.fidelity = 0
        self.is_decoherenced = True
