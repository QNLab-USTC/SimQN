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


class ConstantDelayModel(DelayModel):
    def __init__(self, delay: float = 0, name: Optional[str] = None) -> None:
        """
        A constant delay model

        Args:
            name (str): the name of this delay model
            delay (float): the time delay [s]
        """
        super().__init__(name)
        self._delay = delay

    def calculate(self) -> float:
        """
        Return:
            the time delay [s]
        """
        return self._delay
