from qns.schedular import Event, Simulator
from qns.log import log


class ClassicReceiveEvent(Event):
    def __init__(self, to, msg, source=None, init_time: float = None):
        super().__init__(init_time)
        self.msg = msg
        self.source = source
        self.to = to

    def run(self, simulator: Simulator):
        # self.node.call(simulator, (self.e1, self.e2),
        #  self.source, event=self)
        self.to.call(simulator=simulator, msg=self.msg,
                     source=self.source, event=self)
