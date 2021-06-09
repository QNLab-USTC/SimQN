from qns.schedular import Protocol
from qns.schedular.entity import  *
class Recievepro(Protocol):
    def __init__(self,entity):
            super().__init__(entity)

    def handle(self, simulator, msg: object, source=None, event= None):
        if type(event)==RecieveEvent:
            print(msg)

    




