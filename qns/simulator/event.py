from typing import Optional

from .ts import Time


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


def func_to_event(t: Time, fn, *args, **kwargs):
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
        def __init__(self, t: Optional[Time] = t, name: Optional[str] = None):
            super().__init__(t=t, name=name)

        def invoke(self) -> None:
            fn(*args, **kwargs)

    return WrapperEvent(t)
