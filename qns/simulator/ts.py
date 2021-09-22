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

    __le__ = lambda self, other: self < other or self == other
    __gt__ = lambda self, other: not (self < other or self == other)
    __ge__ = lambda self, other: not (self < other)
    __ne__ = lambda self, other: not self == other


    def __add__(self, ts: Union["Time", float]) -> "Time":
        """
        Add an offset to the Time object

        Args:
            ts (Union["Time", float]): a Time object or a float indicating time in second
        """
        tn = Time(time_slot= self.time_slot, accuracy=self.accuracy)
        if isinstance(ts, float):
            ts = Time(sec = ts, accuracy=self.accuracy)
        tn.time_slot += ts.time_slot
        return tn

    def __repr__(self) -> str:
        return str(self.sec)
