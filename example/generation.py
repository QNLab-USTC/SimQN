from qns.quantum.node import QuantumNodeGenerationProtocol
from qns.schedular.simulator import Simulator
from qns.quantum.link import QuantumChannel, GenerationProtocal
from qns.quantum import QuantumNode

s = Simulator(0,10,1000)

n1 = QuantumNode(20)
n2 = QuantumNode()
ngp1 = QuantumNodeGenerationProtocol(n1)
ngp2 = QuantumNodeGenerationProtocol(n2)

n1.inject_protocol(ngp1)
n2.inject_protocol(ngp2)
n1.install(s)
n2.install(s)

c = QuantumChannel(nodes = [n1, n2], rate = 2, possible= 0.8, delay = 0.02)
gp = GenerationProtocal(c)
c.inject_protocol(gp)
c.install(s)

s.run()