import time
from .event import Event
from .pool import EventsPoolNode, EventsPool

default_start_time = 0.0
default_end_time = 600.0  # seconds
default_time_accuracy = 1000


class SimulatorError(Exception):
    pass


class Simulator():
    '''
    Simulator: The simulator for quantum network.
    '''

    def __init__(self, start_time: float = default_start_time, end_time: float = default_end_time, time_accuracy: int = default_time_accuracy, events_list=[]):
        '''

        :param start_time: simulate start time in second
        :param end_time: simulate end time in second
        :param time_accuracy: simulate time accuracy, eg: 1000, 1000000
        '''
        self.status = "init"
        self.log = None
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
        self.total_events = 0
        self.setup(events_list)

    def run(self):
        '''
        run simulation
        '''
        self.status = "run"
        st = time.time()
        while self.current_time_slice <= self.end_time_slice:
            time_slice, event = self.events_pool.get_event()
            if time_slice is None or event is None:
                break
            self.current_time_slice = time_slice
            self.current_time = self.to_time(self.current_time_slice)
            event.start(self, self.to_time(self.current_time_slice))
        et = time.time()
        self.status = "exit"
        if self.log is not None:
            self.log.info(
                f"runtime {et - st}, {self.total_events} events, sim_time {self.end_time - self.start_time}, x{(self.end_time - self.start_time)/(et-st)}")

    def setup(self, events_list):
        try:
            for el in events_list:
                time, event = el
                self.add_event(self.to_time_slice(time), event)
        except:
            raise SimulatorError("Events List is not vaild")

    def add_event(self, time_slice: int, event: Event):
        '''
        Add an event into simulator event pool.

        :param time_slice: event start time in time_slice
        :param event: inserted event
        '''
        self.events_pool.add_event(time_slice, event)
        self.total_events += 1

    def remote_event(self, event: Event):
        '''
        Remove an event from simulator event pool.

        :param event: removed event
        '''
        self.events_pool.remote_event(event)

    def to_time_slice(self, time: float):
        '''
        Convert time to time_slice, change time from second into inner time sequence

        :param time: a time in second
        :returns: inner time_slice
        '''
        return int(self.time_accuracy * time)

    def to_time(self, time_slice: int) -> float:
        '''
        Convert a time_slice to time
        
        :param time: a time_slice
        :returns: a time in second
        '''
        return time_slice / self.time_accuracy
