from .event import Event
from .pool import EventsPoolNode, EventsPool

default_start_time = 0.0
default_end_time = 600.0  # seconds
default_time_accuracy = 1000


class SimulatorError(Exception):
    pass


class Simulator():
    def __init__(self, start_time: float = default_start_time, end_time: float = default_end_time, time_accuracy: int = default_time_accuracy, events_list=[]):
        self.status = "init"
        self.time_accuracy = time_accuracy

        self.start_time = start_time
        self.start_time_slice = self.to_time_slice(self.start_time)

        self.current_time = self.start_time
        self.current_time_slice = self.start_time_slice

        self.end_time = end_time
        self.end_time_slice = self.to_time_slice(self.end_time)

        self.states = {}  # Used to store state
        self.events_pool = EventsPool(
            self.start_time_slice, self.end_time_slice)
        self.setup(events_list)

    def run(self):
        self.status = "run"
        while self.current_time_slice <= self.end_time_slice:
            time_slice, event = self.events_pool.get_event()
            if time_slice is None or event is None:
                break
            self.current_time_slice = time_slice
            self.current_time = self.to_time(self.current_time_slice)
            event.start(self, self.to_time(self.current_time_slice))
        self.status = "exit"

    def setup(self, events_list):
        try:
            for el in events_list:
                time, event = el
                self.add_event(self.to_time_slice(time), event)
        except:
            raise SimulatorError("Events List is not vaild")

    def add_event(self, time_slice: int, event: Event):
        self.events_pool.add_event(time_slice, event)

    def remote_event(self, event: Event):
        self.events_pool.remote_event(event)

    def to_time_slice(self, time: float):
        return int(self.time_accuracy * time)

    def to_time(self, time_slice: int) -> float:
        return time_slice / self.time_accuracy
