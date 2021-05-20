import random
from enum import Enum
from enum import unique
import uuid


@unique
class Polar(Enum):
    H = 1  # |H> state
    V = 0  # |V> state
    P = 3  # (|H>+|V>)/2 state
    Q = 2  # (|H>-|V>)/2 state
    A = -2  # Isotropy
    N = -1  # not been measured


class Basis(Enum):
    X = 1
    Z = 0


class Photon(object):
    def __init__(self):
        self.is_superposition_state = True
        self.polar: Polar = Polar.A
        self.name = uuid.uuid4()

    def random_preparation(self):
        basis = [Basis.X, Basis.Z][random.randint(0, 1)]
        polar = Polar.A
        if basis == Basis.X:
            polar = [Polar.H, Polar.V][random.randint(0, 1)]
        else:
            polar = [Polar.P, Polar.Q][random.randint(0, 1)]
        self.preparation(polar)
        return basis, polar

    def random_measure(self):
        basis = [Basis.X, Basis.Z][random.randint(0, 1)]
        polar = self.measure(basis)
        return basis, polar

    def preparation(self, polar: Polar):
        if self.is_superposition_state:
            self.polar = polar

    def measure(self, basis: Basis):
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
