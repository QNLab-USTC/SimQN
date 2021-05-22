import random
from typing import Tuple
from enum import Enum
from enum import unique
import uuid


@unique
class Polar(Enum):
    '''
    ``Polar`` is the quantum state of a single photon

    :var H: \|1> state
    :var V: \|0> state
    :var P: \|+> state
    :var Q: \|-> state
    :var A: Any state
    :var N: Not be measured
    '''
    H = 1  # |H> state
    V = 0  # |V> state
    P = 3  # (|H>+|V>)/2 state
    Q = 2  # (|H>-|V>)/2 state
    A = -2  # Isotropy
    N = -1  # not been measured


class Basis(Enum):
    '''
    ``Basis`` is the quantum basis

    :var X: X basis
    :var Z: Z basis
    '''
    X = 1
    Z = 0


class Photon(object):
    '''
    This is a single photon

    :var bool is_superposition_state: whether this photon is in super position state
    :var Polar polar: its polar state
    :var str name: its name
    '''

    def __init__(self):
        self.is_superposition_state = True
        self.polar: Polar = Polar.A
        self.name = uuid.uuid4()

    def random_preparation(self) -> Tuple[Basis, Polar]:
        '''
        randomly use a basis and generate the transmit its linear polarization

        :returns: the basis and the polar
        '''
        basis = [Basis.X, Basis.Z][random.randint(0, 1)]
        polar = Polar.A
        if basis == Basis.X:
            polar = [Polar.H, Polar.V][random.randint(0, 1)]
        else:
            polar = [Polar.P, Polar.Q][random.randint(0, 1)]
        self.preparation(polar)
        return basis, polar

    def random_measure(self) -> Tuple[Basis, Polar]:
        '''
        randomly use a basis measure its linear polarization

        :returns: the basis and the polar
        '''
        basis = [Basis.X, Basis.Z][random.randint(0, 1)]
        polar = self.measure(basis)
        return basis, polar

    def preparation(self, polar: Polar):
        '''
        Set this photon into certain polarization

        :param Polar polar: its polarizaion
        '''
        if self.is_superposition_state:
            self.polar = polar

    def measure(self, basis: Basis):
        '''
        Measure its polarization using selected basis.

        :param Basis basis: the selected basis
        :returns: 1 or 0 to present its polarization. -2 means not been measured.
        '''
        if not self.is_superposition_state:
            return None

        self.is_superposition_state = False

        if self.polar is Polar.A:
            return Polar.A.value

        if basis == Basis.X:
            if self.polar in [Polar.H, Polar.V]:
                return self.polar.value
            return Polar.N.value

        if self.polar in [Polar.P, Polar.Q]:
            return self.polar.value - 2
        return Polar.N.value

    def __repr__(self) -> str:
        return f"<{self.name} is_measured:{not self.is_superposition_state} polar: {self.polar}>"
