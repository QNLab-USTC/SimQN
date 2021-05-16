from qns.quantum.node import QuantumNodeGenerationProtocol, QuantumNodeSwappingProtocol
from qns.schedular.simulator import Simulator
from qns.quantum.link import QuantumChannel, GenerationProtocal
from qns.quantum import QuantumNode
from qns.quantum import QuantumNetwork

s = Simulator(0,10,10000)

n1 = QuantumNode()
ngp1 = QuantumNodeGenerationProtocol(n1)
nsp1 = QuantumNodeSwappingProtocol(n1)
n1.inject_protocol([ngp1, nsp1])

n2 = QuantumNode()
ngp2 = QuantumNodeGenerationProtocol(n2)
nsp2 = QuantumNodeSwappingProtocol(n2)
n2.inject_protocol([ngp2, nsp2])

n3 = QuantumNode()
ngp3 = QuantumNodeGenerationProtocol(n3)
nsp3 = QuantumNodeSwappingProtocol(n3)
n3.inject_protocol([ngp3, nsp3])

n2.route = [[n1], [n3]]

n1.install(s)
n2.install(s)
n3.install(s)

c1 = QuantumChannel(nodes = [n1, n2], rate = 5, possible= 0.8, delay = 0.65)
cgp1 = GenerationProtocal(c1)
c1.inject_protocol(cgp1)
c1.install(s)

c2 = QuantumChannel(nodes = [n2, n3], rate = 5, possible= 0.8, delay = 0.64)
cgp2 = GenerationProtocal(c2)
c2.inject_protocol(cgp2)
c2.install(s)

s.run()
count = 0
for e in n3.registers:
    if n1 in e.nodes:
        count += 1
print(count)