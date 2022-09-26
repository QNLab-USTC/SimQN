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
from qns.models.qubit.const import QUBIT_STATE_0
from qns.models.qubit.gate import I, X, Y, Z
import numpy as np
from qns.models.qubit.qubit import QState
from qns.utils.rnd import get_rand


def PrefectError(self, p: Optional[float] = 0, **kwargs):
    """
    The default error model for this qubit.

    Args:
        p (float): the error possibility
    """
    pass


def DephaseError(self, p: Optional[float] = 0, **kwargs):
    """
    The dephase error model.
    A random Z gate will be operate on the qubit with possibility p.

    Args:
        p (float): the error possibility
    """
    if p < 0 or p > 1:
        raise Exception("Error decoherence rate, should be in [0, 1]")
    self.stochastic_operate([I, Z], [1-p, p])


def DepolarError(self, p: Optional[float] = 0, **kwargs):
    """
    The depolarizing error model.

    One of the random Pauli gate will be operate on the qubit with possibility p :

    Args:
        p (float): the error possibility
        kwargs: other parameters
    """
    if p < 0 or p > 1:
        raise Exception("Error decoherence rate, should be in [0, 1]")
    if 1-3*p > 0:
        self.stochastic_operate([I, X, Y, Z], [1-3*p, p, p, p])
    else:
        self.stochastic_operate([X, Y, Z], [1/3, 1/3, 1/3])


def BitFlipError(self, p: Optional[float] = 0, **kwargs):
    """
    The bit flip error model.

    Args:
        p (float): the error possibility, [0, 1]
        kwargs: other parameters
    """
    if p < 0 or p > 1:
        raise Exception("Error decoherence rate, should be in [0, 1]")
    self.stochastic_operate([I, X], [1-p, p])


def DissipationError(self, p: Optional[float] = 0, **kwargs):
    """
    The dissipation error model.

    Args:
        p (float): the error possibility, [0, 1]
        kwargs: other parameters
    """
    if p < 0 or p > 1:
        raise Exception("Error decoherence rate, should be in [0, 1]")
    real_p = get_rand()
    if real_p < p:
        self.measure()
        self.state = QState([self], state=QUBIT_STATE_0)


def ErrorWithTime(ErrorModel):
    """generate the error. The error possibility is 1-e^{-decoherence_rate * t}"""
    def GeneratedErrorWithTime(self, t: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
        """
        The error model with time for this qubit. The error possibility is 1-e^{-decoherence_rate * t}.

        Args:
            t (float): the during time in second.
            decoherence_rate (float): the decoherence rate.
        """
        p = 1 - np.exp(-decoherence_rate * t)
        ErrorModel(self, p, **kwargs)
    return GeneratedErrorWithTime


def ErrorWithLength(ErrorModel):
    """generate the error. The error possibility is 1-e^{-decoherence_rate * length}"""
    def GeneratedErrorWithLength(self, length: Optional[float] = 0, decoherence_rate: Optional[float] = 0, **kwargs):
        """
        The error model with length for this qubit. The error possibility is 1-e^{-decoherence_rate * length}.

        Args:
            length (float): the transmission length in meter.
            decoherence_rate (float): the decoherence rate.
        """
        p = 1 - np.exp(-decoherence_rate * length)
        ErrorModel(self, p, **kwargs)
    return GeneratedErrorWithLength


PrefectStorageErrorModel = ErrorWithTime(PrefectError)
PrefectTransferErrorModel = ErrorWithLength(PrefectError)
PrefectOperateErrorModel = PrefectError
PrefectMeasureErrorModel = PrefectError

DephaseStorageErrorModel = ErrorWithTime(DephaseError)
DephaseTransferErrorModel = ErrorWithLength(DephaseError)
DephaseOperateErrorModel = DephaseError
DephaseMeasureErrorModel = DephaseError

DepolarStorageErrorModel = ErrorWithTime(DepolarError)
DepolarTransferErrorModel = ErrorWithLength(DepolarError)
DepolarOperateErrorModel = DepolarError
DepolarMeasureErrorModel = DepolarError

BitFlipStorageErrorModel = ErrorWithTime(BitFlipError)
BitFilpTransferErrorModel = ErrorWithLength(BitFlipError)
BitFlipOperateErrorModel = BitFlipError
BitFlipMeasureErrorModel = BitFlipError

DissipationStorageErrorModel = ErrorWithTime(DissipationError)
DissipationTransferErrorModel = ErrorWithLength(DissipationError)
DissipationOperateErrorModel = DissipationError
DissipationMeasureErrorModel = DissipationError
