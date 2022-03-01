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
#    along with this program. If not, see <https://www.gnu.org/licenses/>.


from typing import Optional
from qns.models.qubit.gate import I, X, Y, Z
import numpy as np


def PrefectStorageErrorModel(self, t: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The default error model for storing a qubit in quantum memory.
    The default behavior is doing nothing

    Args:
        t: the time stored in a quantum memory. The unit it second.
        decoherence_rate (float): the decoherence rate.
        kwargs: other parameters
    """
    pass


def DephaseStorageErrorModel(self, t: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The dephase error model for storing a qubit in quantum memory.

    A random Z gate will be operate on the qubit with possibility: 1-e^(-decoherence_rate * t)

    Args:
        t: the time stored in a quantum memory. The unit it second.
        decoherence_rate (float): the decoherence rate
        kwargs: other parameters
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate * t)
    self.stochastic_operate([I, Z], [1-p, p])


def DepolarStorageErrorModel(self, t: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The depolar error model for storing a qubit in quantum memory.

    One of the random Pauli gate will be operate on the qubit with possibility:
        1-e^(-decoherence_rate * t)

    Args:
        t: the time stored in a quantum memory. The unit it second.
        decoherence_rate (float): the decoherence rate
        kwargs: other parameters
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate * t)
    if 1-3*p > 0:
        self.stochastic_operate([I, X, Y, Z], [1-3*p, p, p, p])
    else:
        self.stochastic_operate([X, Y, Z], [1/3, 1/3, 1/3])


def PrefectTransferErrorModel(self, length: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The default error model for transmitting this qubit
    The default behavior is doing nothing

    Args:
        length (float): the length of the channel
        decoherence_rate (float): the decoherence rate.
        kwargs: other parameters
    """
    pass


def DephaseTransferErrorModel(self, length: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The dephase error model for transmitting a qubit in quantum channel.

    A random Z gate will be operate on the qubit with possibility: 1-e^(-decoherence_rate * length)

    Args:
        length: the channel length
        decoherence_rate (float): the decoherence rate
        kwargs: other parameters
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate * length)
    self.stochastic_operate([I, Z], [1-p, p])


def DepolarTransferErrorModel(self, length: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The depolar error model for transmitting a qubit in quantum channel.

    One of the random Pauli gate will be operate on the qubit with possibility:
        1-e^(-decoherence_rate * t)

    Args:
        length: the channel length
        decoherence_rate (float): the decoherence rate
        kwargs: other parameters
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate * length)
    if 1-3*p > 0:
        self.stochastic_operate([I, X, Y, Z], [1-3*p, p, p, p])
    else:
        self.stochastic_operate([X, Y, Z], [1/3, 1/3, 1/3])


def PrefectOperateErrorModel(self, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The default error model for operating this qubit.

    Args:
        decoherence_rate (float): the decoherence rate
    """
    pass


def DephaseOperateErrorModel(self, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The dephase error model for operating this qubit.
    A random Z gate will be operate on the qubit with possibility: 1-e^(-decoherence_rate)

    Args:
        decoherence_rate (float): the decoherence rate
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate)
    self.stochastic_operate([I, Z], [1-p, p])


def DepolarOperateErrorModel(self, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The depolar error model for operating on a qubit.

    One of the random Pauli gate will be operate on the qubit with possibility:
        1-e^(-decoherence_rate * t)

    Args:
        decoherence_rate (float): the decoherence rate
        kwargs: other parameters
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate)
    if 1-3*p > 0:
        self.stochastic_operate([I, X, Y, Z], [1-3*p, p, p, p])
    else:
        self.stochastic_operate([X, Y, Z], [1/3, 1/3, 1/3])


def PrefectMeasureErrorModel(self, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The default error model for measuring this qubit.

    Args:
        decoherence_rate (float): the decoherence rate
    """
    pass


def DephaseMeasureErrorModel(self, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The dephase error model for measuring this qubit,
    A random Z gate will be operate on the qubit with possibility: 1-e^(-decoherence_rate)

    Args:
        decoherence_rate (float): the decoherence rate
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate)
    self.stochastic_operate([I, Z], [1-p, p])


def DepolarMeasureErrorModel(self, decoherence_rate: Optional[float] = 0, **kwargs):
    """
    The depolar error model for measuring on a qubit.

    One of the random Pauli gate will be operate on the qubit with possibility:
        1-e^(-decoherence_rate * t)

    Args:
        decoherence_rate (float): the decoherence rate
        kwargs: other parameters
    """
    if decoherence_rate < 0:
        raise Exception("Error decoherence rate, should be positive")
    p = 1 - np.exp(-decoherence_rate)
    if 1-3*p > 0:
        self.stochastic_operate([I, X, Y, Z], [1-3*p, p, p, p])
    else:
        self.stochastic_operate([X, Y, Z], [1/3, 1/3, 1/3])
