from .event import Event

default_start_time = 0.0
default_end_time = 600.0  # UINT64_MAX
default_time_accuracy = 1000

class SimulatorError(Exception):
    pass

class Simulator():
    def __init__(self, start_time: float=default_start_time, end_time: float=default_end_time, time_accuracy: int=default_time_accuracy, events_list = []):
        self.start_time = start_time
        self.end_time = end_time
        self.time_accuracy = time_accuracy

        self.start_time_slice = self.to_time_slice(self.start_time)
        self.current_time_slice = self.start_time_slice
        self.end_time_slice = self.to_time_slice(self.end_time)
        self.states = {} # Used to store state
        self.events_pool = {}
        self.setup(events_list)

    def run(self):
        while self.current_time_slice <= self.end_time_slice:
            events = self.get_events(self.current_time_slice)
            for event in events:
                event.start(self, self.to_time(self.current_time_slice))
            self.current_time_slice += 1

    def setup(self, events_list):
        try:
            for el in events_list:
                time, event = el
                self.add_event(self.to_time_slice(time), event)
        except:
            raise SimulatorError("Events List is not vaild")

    def get_events(self, time_slice: int = None):
        if time_slice is None:
            ret = []
            for _,v in self.end_time:
                ret.extend(v)
            return ret
        return self.events_pool.get(time_slice, [])

    def add_event(self, time_slice: int, event: Event):
        if self.events_pool.get(time_slice) is None:
            self.events_pool[time_slice] = []
        self.events_pool[time_slice].append(event)

    def remote_event(self, event: Event, time_slice: int = None):
        if time_slice is not None:
            if event in self.events_pool[time_slice]:
                self.events_pool.remove(event)
        else:
            for t in self.events_pool.keys():
                self.events_pool[t].remove(event)
        
    def clear_event(self, time = None):
        if time is not None:
            self.events_pool[time] = []
        else:
            self.events_pool = {}

    def to_time_slice(self, time: float):
        return int(self.time_accuracy * time)
    
    def to_time(self, time_slice: int) -> float:
        return time_slice / self.time_accuracy
