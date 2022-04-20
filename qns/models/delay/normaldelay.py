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

from typing import Optional
from qns.models.delay.delay import DelayModel
from qns.utils.rnd import get_normal


class NormalDelayModel(DelayModel):
    def __init__(self, mean_delay: float = 0, std: float = 0, name: Optional[str] = None) -> None:
        """
        A random delay from normal distribution X~N(mean_delay, std^2)

        Args:
            name (str): the name of this delay model
            mean_delay (float): the mean of the time delay [s]
            std (float): the standand deviation [s]
        """
        super().__init__(name)
        self._mean_delay = mean_delay
        self._std = std

    def calculate(self) -> float:
        return get_normal(self._mean_delay, self._std)
