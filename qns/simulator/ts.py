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

from typing import Union


default_accuracy = 1000000  # {default_accuracy} time slots per second


class Time(object):
    def __init__(self, time_slot: int = 0, sec: float = 0.0, accuracy: int = default_accuracy):
        '''
        Time: the time slot used in the simulator

        Args:
            time_slot (int): the time slot
            sec (float): the timestamp in second
            accuracy: time slots per second
        '''
        self.accuracy = accuracy
        if time_slot != 0:
            self.time_slot = time_slot
        else:
            if sec is None:
                sec = 0
            self.time_slot = int(sec * self.accuracy)

    @property
    def sec(self) -> float:
        '''
        Returns:
            the timestamp in second
        '''
        return self.time_slot / self.accuracy

    def __eq__(self, other: object) -> bool:
        return self.time_slot == other.time_slot

    def __lt__(self, other: object) -> bool:
        return self.time_slot < other.time_slot

    def __le__(self, other: object) -> bool:
        return self < other or self == other

    def __gt__(self, other: object) -> bool:
        return not (self < other or self == other)

    def __ge__(self, other: object) -> bool:
        return not (self < other)

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __add__(self, ts: Union["Time", float]) -> "Time":
        """
        Add an offset to the Time object

        Args:
            ts (Union["Time", float]): a Time object or a float indicating time in second
        """
        tn = Time(time_slot=self.time_slot, accuracy=self.accuracy)
        if isinstance(ts, float):
            ts = Time(sec=ts, accuracy=self.accuracy)
        tn.time_slot += ts.time_slot
        return tn

    def __repr__(self) -> str:
        return str(self.sec)
