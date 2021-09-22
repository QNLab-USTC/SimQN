class QuantumModel(object):
    """
    The interface to present the backend models, including qubit, epr and other models.
    """
    def storage_error_model(self, t: float = 0, **kwargs):
        """
        The error model for quantum memory.
        This function will change the quantum state or fidelity according to different backend models.

        Args:
            t: the time stored in a quantum memory. The unit it second.
            kwargs: other parameters
        """
        raise NotImplemented

    def transfer_error_model(self, length: float, **kwargs):
        """
        The error model for transmitting a qubit in quantum channel.
        This function will change the quantum state or fidelity according to different backend models.

        Args:
            length (float): the length of the channel 
            kwargs: other parameters
        """
        raise NotImplemented