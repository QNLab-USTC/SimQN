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


def PrefectStorageErrorModel(self, t: float, **kwargs):
    """
    The default error model for storing a qubit in quantum memory.
    The default behavior is doing nothing

    Args:
        t: the time stored in a quantum memory. The unit it second.
        kwargs: other parameters
    """
    pass


def PrefectTransferErrorModel(self, length: float, **kwargs):
    """
    The default error model for transmitting this qubit
    The default behavior is doing nothing

    Args:
        length (float): the length of the channel
        kwargs: other parameters
    """
    pass

def measure_error_model(self, **kwargs):
    """
    The default error model for measuring this qubit.
    The default behavior is doing nothing

    Args:
        kwargs: parameters
    """
    pass

def operating_error_model(self, **kwargs):
    """
    The default error model for operating this qubit,
    which is called whenever this qubit operates a quantum gate
    The default behavior is doing nothing

    Args:
        t: the time to measure this qubit
    """
    pass