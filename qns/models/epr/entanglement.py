
from typing import List, Optional
import numpy as np
from ..qubit import H, X, Y, Z, CNOT, Qubit, QState, QUBIT_STATE_0, QUBIT_STATE_P


class BaseEntanglement(object):
    """
    This is the base entanglement model
    """
    def __init__(self, fidelity: float = 1 ,name: Optional[str] = None):
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
            the new distributed entnaglement
        """
        raise NotImplemented

    def distillation(self, epr: "BaseEntanglement") -> "BaseEntanglement":
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entnaglement
        """
        raise NotImplemented

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
        qs = QState([q0, q1], state =np.array([[a], [b], [b], [a]]))
        q0.state = qs
        q1.state = qs
        return [q0, q1]

    def teleportion(self, qubit: Qubit) -> Qubit:
        """
        Use `self` and `epr` to perfrom distillation and distribute a new entanglement

        Args:
            epr (BaseEntanglement): another entanglement
        Returns:
            the new distributed entnaglement
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

class BellStateEntanglement(BaseEntanglement):
    """
    `BellStateEntanglement` is the ideal max entangled qubits. Its fidelity is always 1.
    """
    def swapping(self, epr: "BellStateEntanglement"):
        ne = BellStateEntanglement()
        if self.is_decoherenced == True or epr.is_decoherenced == True:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        return ne
    
    def distillation(self, epr: "BellStateEntanglement"):
        ne = BellStateEntanglement()
        if self.is_decoherenced == True or epr.is_decoherenced == True:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        return ne

class WernerStateEntanglement(BaseEntanglement):
    """
    `WernerStateEntanglement` is a pair of entangled qubits in Werner State with a hidden-variable.
    """
    def __init__(self, fidelity: float = 1,name: Optional[str] = None):
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

    def swapping(self, epr: "WernerStateEntanglement"):
        ne = WernerStateEntanglement()
        if self.is_decoherenced == True or epr.is_decoherenced == True:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        ne.w = self.w * epr.w
        return ne
    
    def distillation(self, epr: "BellStateEntanglement"):
        ne = BellStateEntanglement()
        if self.is_decoherenced == True or epr.is_decoherenced == True:
            ne.is_decoherenced = True
            ne.fidelity = 0
        epr.is_decoherenced = True
        self.is_decoherenced = True
        return ne