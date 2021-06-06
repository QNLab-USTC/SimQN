
from qns.schedular import Entity,Event
from qns.schedular.entity import RecieveEvent

class Node(Entity):
    '''
    This is the classes for a quantum node (routers, repeaters or clients).
    Its behavior should be injected by ``qns.schedular.Protocol``

    :param str name: its name
    '''

    def __init__(self, name = None):
        super().__init__(name)
    def handle(self, simulator, msg, source=None, event=None):
        if type(event)==RecieveEvent:
            print(msg[0].polar)
    def __repr__(self) -> str:
        return f"<node {self.name}>"





    

