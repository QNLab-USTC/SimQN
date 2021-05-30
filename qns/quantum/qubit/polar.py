from enum import Enum, unique

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