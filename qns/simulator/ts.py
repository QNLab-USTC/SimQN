default_accuracy = 1000000  # {default_accuracy} time slots per second
default_start_time = 0.0
default_end_time = 60.0


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
            self.time_slot = 0
        else:
            self.time_slot = int(sec * self.accuracy)

    @property
    def sec(self) -> float:
        '''
        Returns:
            the timestamp in second
        '''
        return self.time_slot / self.accuracy

    def __eq__(self, t: "Time") -> bool:
        return self.time_slot == t.time_slot

    def __lt__(self, t: "Time") -> bool:
        return self.time_slot < t.time_slot

    def __repr__(self) -> str:
        return str(self.sec)
