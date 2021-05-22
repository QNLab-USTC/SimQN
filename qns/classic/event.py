from qns.schedular import Event, Simulator
from qns.log import log


class ClassicReceiveEvent(Event):
    '''
    The event that calls the receiver to receive the classic message

    :param to: the receiver node
    :param msg: the classic message
    '''

    def __init__(self, to, msg, source=None, init_time: float = None):
        super().__init__(init_time)
        self.msg = msg
        self.source = source
        self.to = to

    def run(self, simulator: Simulator):
        self.to.call(simulator=simulator, msg=self.msg,
                     source=self.source, event=self)
