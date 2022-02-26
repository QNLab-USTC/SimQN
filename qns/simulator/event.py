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

from qns.simulator.ts import Time


class Event(object):
    """
    Basic event class in simulator
    """

    def __init__(self, t: Optional[Time] = None, name: Optional[str] = None):
        """
        Args:
            t (Time): the time slot of this event
            name (str): the name of this event
        """
        self.t: Optional[Time] = t
        self.name: Optional[str] = name
        self._is_canceled: bool = False

    def invoke(self) -> None:
        """
        Invoke the event, should be implemented
        """
        raise NotImplementedError

    def cancel(self) -> None:
        """
        Cancel this event
        """
        self._is_canceled = True

    @property
    def is_canceled(self) -> bool:
        """
        Returns:
            whether this event has been canceled
        """
        return self._is_canceled

    def __eq__(self, other: object) -> bool:
        return self.t == other.t

    def __lt__(self, other: object) -> bool:
        return self.t < other.t

    def __le__(self, other: Time) -> bool:
        return self < other or self == other

    def __gt__(self, other: Time) -> bool:
        return not (self < other or self == other)

    def __ge__(self, other: Time) -> bool:
        return not (self < other)

    def __ne__(self, other: Time) -> bool:
        return not self == other

    def __repr__(self) -> str:
        if self.name is not None:
            return f"Event({self.name})"
        return "Event()"


def func_to_event(t: Time, name, fn, *args, **kwargs):
    """
    Convert a function to an event, the function `fn` will be called at `t`.
    It is a simple method to wrap a function to an event.

    Args:
        t (Time): the function will be called at `t`
        fn (Callable): the function
        *args: the function's parameters
        **kwargs: the function's parameters
    """

    class WrapperEvent(Event):
        def __init__(self, t: Optional[Time] = t, name_event = name):
            super().__init__(t=t, name=name_event)

        def invoke(self) -> None:
            fn(*args, **kwargs)

    return WrapperEvent(t)
