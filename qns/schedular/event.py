class Event():
    '''
    The class is the structure of an event.

    :param init_time: the event's generation time in second
    :var start_time: the event's start time in second
    :var end_time: the event's end time in second
    :var source: the entity that triggle this event
    '''

    def __init__(self, init_time: float = None):
        self.done: bool = False
        self.init_time: float = 0
        self.start_time: float = None
        self.end_time: float = None
        self.source: Event = None

    def start(self, simulator, start_time=None):
        '''
        It is an inner function is called by ``simulator``, it calles ``run`` to carry out actions.

        :param simulator: the simulator
        :param start_time: the real event's start time
        '''
        self.start_time = start_time
        self.end_time = start_time
        self.run(simulator)

    def run(self, simulator):
        '''
        It is the real event's handle functions. ``run`` should be overrided.

        :param simulator: the simulator.
        '''
        raise NotImplemented

    def cancel(self, *args, **kwargs):
        '''
        It is the cancel function. If this function is implemented, the event can be canceled.
        '''
        pass
