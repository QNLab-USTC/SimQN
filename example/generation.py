from qns.schedular.simulator import Simulator
from qns.quantum.link import QuantumChannel
from qns.quantum import QuantumNode
from qns.quantum import QuantumNetwork

s = Simulator(0,10,1000)

n1 = QuantumNode(20)
n2 = QuantumNode()
n1.install(s)
n2.install(s)

c = QuantumChannel(nodes = [n1, n2], rate = 2, possible= 0.8, delay = 0.02)
c.install(s)

s.run()