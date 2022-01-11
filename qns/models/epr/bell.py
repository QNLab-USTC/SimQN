from typing import Optional
import random

from qns.models.core.backend import QuantumModel
from qns.models.epr.entanglement import BaseEntanglement


class BellStateEntanglement(BaseEntanglement, QuantumModel):
    """
    `BellStateEntanglement` is the ideal max entangled qubits. Its fidelity is always 1.
    """

    def __init__(self, fidelity: float = 1, name: Optional[str] = None, p_swap: float = 1):
        super().__init__(fidelity=1, name=name)
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
