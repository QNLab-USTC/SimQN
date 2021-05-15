from qns.schedular.simulator import Simulator
from qns.quantum.link import QuantumChannel
from qns.quantum import QuantumNode
from qns.quantum import QuantumNetwork

s = Simulator(0,10,100000)

n1 = QuantumNode()
n2 = QuantumNode(10)
n3 = QuantumNode()
n2.route = [[n1], [n3]]

n1.install(s)
n2.install(s)
n3.install(s)

c1 = QuantumChannel(nodes = [n1, n2], rate = 2, possible= 0.8, delay = 0.03)
c1.install(s)

c2 = QuantumChannel(nodes = [n2, n3], rate = 2, possible= 0.8, delay = 0.03)
c2.install(s)

s.run()
count = 0
for e in n3.registers:
    if n1 in e.nodes:
        count += 1
print(count)