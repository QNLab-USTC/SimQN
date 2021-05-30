
from qns.schedular import Entity

class Node(Entity):
    '''
    This is the classes for a quantum node (routers, repeaters or clients).
    Its behavior should be injected by ``qns.schedular.Protocol``

    :param str name: its name
    '''

    def __init__(self, name = None):
        super().__init__(name)

    def __repr__(self) -> str:
        return f"<node {self.name}>"