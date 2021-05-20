from hashlib import new
from qns.schedular import Event
from qns.schedular import Simulator


class GenerationAndSendEvent(Event):
    def __init__(self, protocol, source=None, init_time: float = None):
        super().__init__(init_time)
        self.protocol = protocol
        self.source = source

    def run(self, simulator: Simulator):
        # self.node.call(simulator, (self.e1, self.e2),
        #  self.source, event=self)
        self.protocol.run(simulator, self)


class PhotonReceiveEvent(Event):
    def __init__(self, to, new_photon, source=None, init_time: float = None):
        super().__init__(init_time)
        self.photon = new_photon
        self.source = source
        self.to = to

    def run(self, simulator: Simulator):
        # self.node.call(simulator, (self.e1, self.e2),
        #  self.source, event=self)
        self.to.call(simulator=simulator, msg=self.photon,
                     source=self.source, event=self)
