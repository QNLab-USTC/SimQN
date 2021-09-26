from .entity import Entity

class QNode(Entity):
    def __init__(self, name: str = None):
        super().__init__(name=name)

        self.cchannels = []
        self.qchannels = []
        self.memories = []