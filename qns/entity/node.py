from .entity import Entity

class QNode(Entity):
    """
    QNode is a quantum node in the quantum network
    """
    def __init__(self, name: str = None):
        super().__init__(name=name)

        self.cchannels = []
        self.qchannels = []
        self.memories = []

        self.croute_table = []
        self.qroute_table = []
