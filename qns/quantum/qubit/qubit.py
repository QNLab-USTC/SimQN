import uuid
from .polar import Polar
from .basis import Basis

class QubitFidelityInvaildError(Exception):
    pass

class QubitRemoveEntanglementError(Exception):
    pass

class Qubit(object):
    '''
    This is the qubit class in quantum model

    :param birth_time_slice: its birth time slice
    :param fidelity: its fidelity
    :param live_func: inject a ``live_func`` to determine whether this qubit is decohered.
    :param name: its name
    '''
    def __init__(self, birth_time_slice: int, fidelity: float = 1, live_func = None, name: str = None):
        self.birth_time_slice = birth_time_slice

        self.fidelity = fidelity
        self.polar = None
        self.entangled: list[Qubit] = []
        self.denityMatric = None
        
        self.live_func = live_func

        if name is None:
            self.name = uuid.uuid4()
        else:
            self.name = name

        
    def is_live(self) -> bool:
        '''
        Returns whether it is decohered.
        If ``live_func`` is injected, this self-defined function will be used.
        Or it will always return `self.fidelity >= 0.5`.

        :returns: bool, `true` if it is still not decohered.
        '''
        if self.live_func is not None:
            return self.live_func()
        return self.fidelity >= 0.5

    def is_entangled(self) -> bool:
        '''
        Returns whether it is entangled with other qubits.
        :returns: bool, `true` if it is entangled
        '''
        return len(self.entangled)

    def set_fidelity(self, fidelity: float):
        '''
        Set its fidelity
        '''
        if fidelity < 0 or fidelity > 1:
            raise QubitFidelityInvaildError

    def set_polar(self, polar: Polar):
        '''
        Set its polar

        :param polar: the polarization of this qubit
        '''
        self.polar = polar

    def add_entanglement(self, qubit):
        '''
        add an entangled qubit

        :param qubit: another qubit that entangled with `self`
        '''
        self.entangled.append(qubit)

    
    def remove_entanglement(self, qubit):

        try:
            self.entangled.remove(qubit)
        except ValueError:
            raise QubitRemoveEntanglementError(f"{qubit} is not entangled with {self}")

    
    def __repr__(self) -> str:
        return f"<qubit {self.name}, fidelity: {self.fidelity}>"

