
default_start_time = 0
default_end_time = 4294967295  # UINT64_MAX
default_time_accuracy = 1000


class schedular():
    def __init__(self, start_time=default_start_time, end_time=default_end_time, time_accuracy=default_time_accuracy, events=[]):
        self.start_time = start_time
        self.end_time = end_time
        self.time_accuracy = time_accuracy
        self.events = []

    def run(self):
        raise NotImplemented

    def setup(self):
        raise NotImplemented