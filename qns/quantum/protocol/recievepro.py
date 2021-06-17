from qns.quantum.protocol import NodeProtocol
from qns.schedular.entity import  *
from qns.schedular import Simulator


class Recievepro(NodeProtocol):

    def run(self, simulator: Simulator):
        i = 0
        while True:
            (msg, source, event) =  yield None
            print(f"{i}th called")
            print(msg)
            i+=1


        

    




