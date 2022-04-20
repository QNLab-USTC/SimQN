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
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import random
from typing import Optional
import numpy as np


def set_seed(seed: Optional[int] = None):
    """
    Set a seed for random generator

    Args:
        seed (int): the seed
    """
    if seed is None:
        return
    random.seed(seed)
    np.random.seed(seed)


def get_rand(low: float = 0, high: float = 1) -> float:
    """
    Get a random number from [low, high)

    Args:
        low (int): the low bound
        high (int): the high bound
    """
    return low + np.random.random() * (high - low)


def get_randint(low: int, high: int) -> float:
    """
    Get a random integer from [low, high]

    Args:
        low (int): the low bound
        high (int): the high bound
    """
    if low != int(low):
        raise ValueError("input low")
    if low > high:
        raise ValueError("low should smaller than high")
    return np.random.randint(low, high+1)


def get_choice(a):
    """
    return an random element from a list

    Args:
        a: a iterable object
    """
    return a[get_randint(0, len(a)-1)]


def get_normal(mean: float = 0, std: float = 1):
    return np.random.normal(loc=mean, scale=std)
