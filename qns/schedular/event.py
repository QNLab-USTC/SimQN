# This is the Event object that is dispatched by the simulator
class Event():
    def __init__(self, init_time: float = None):
        self.done: bool = False
        self.init_time: float= 0
        self.start_time: float = None
        self.end_time: float = None
        self.source: Event = None

    def start(self, simulator, start_time = None):
        self.start_time = start_time
        self.run(simulator)

    def run(self, simulator):
        raise NotImplemented

    def cancel(self, *args, **kwargs):
        pass