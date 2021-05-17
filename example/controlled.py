from os import name
from qns.schedular import Simulator, Protocol
from qns.quantum import QuantumNode, QuantumController, QuantumChannel, GenerationProtocal, QuantumNodeSwappingProtocol, QuantumNodeDistillationProtocol, ControllerProtocol
from qns.log import log


class PrintProtocol(Protocol):
    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        self = _self.entity
        count = 0
        log.info("check {}: {}", self, self.registers)


s = Simulator(0, 5, 100000)
log.set_debug(True)
log.install(s)

n1 = QuantumNode(name="n1", registers_number=40)
nsp1 = QuantumNodeSwappingProtocol(n1, under_controlled=True)
ndp1 = QuantumNodeDistillationProtocol(
    n1, threshold=0.9, under_controlled=True)
npp1 = PrintProtocol(n1)
n1.inject_protocol([ndp1, nsp1])

n2 = QuantumNode(name="n2", registers_number=40)
nsp2 = QuantumNodeSwappingProtocol(n2, under_controlled=True)
ndp2 = QuantumNodeDistillationProtocol(
    n2, threshold=0.9, under_controlled=True)
npp2 = PrintProtocol(n2)
n2.inject_protocol([ndp2, nsp2])

n3 = QuantumNode(name="n3", registers_number=40)
nsp3 = QuantumNodeSwappingProtocol(n3, under_controlled=True)
ndp3 = QuantumNodeDistillationProtocol(
    n3, threshold=0.9, under_controlled=True)
npp3 = PrintProtocol(n3)
n3.inject_protocol([ndp3, nsp3])

n4 = QuantumNode(name="n4", registers_number=40)
nsp4 = QuantumNodeSwappingProtocol(n4, under_controlled=True)
ndp4 = QuantumNodeDistillationProtocol(
    n4, threshold=0.9, under_controlled=True)
npp4 = PrintProtocol(n4)
n4.inject_protocol([ndp4, nsp4])

n1.install(s)
n2.install(s)
n3.install(s)
n4.install(s)

# n2.route = [[n1], [n3, n4]]
# n3.route = [[n1, n2], [n4]]
# n1.allow_distillation = [n3, n2]
# n2.allow_distillation = [n3]
# n4.allow_distillation = [n2, n3]


c1 = QuantumChannel(nodes=[n1, n2], name="c1")
cgp1 = GenerationProtocal(c1, rate=50, possible=0.8, fidelity=0.93)
c1.inject_protocol(cgp1)
c1.install(s)

c2 = QuantumChannel(nodes=[n2, n3], name="c2")
cgp2 = GenerationProtocal(c2, rate=50, possible=0.8, fidelity=0.93)
c2.inject_protocol(cgp2)
c2.install(s)

c3 = QuantumChannel(nodes=[n3, n4], name="c3")
cgp3 = GenerationProtocal(c3, rate=50, possible=0.8, fidelity=0.93)
c3.inject_protocol(cgp3)
c3.install(s)

controller = QuantumController(nodes=[n1, n2, n3, n4], links=[
                               c1, c2, c3], name="controller")
distillation_schema = [(n1, n2), (n1, n3), (n1, n4),
                       (n2, n3), (n2, n4), (n3, n4)]
swapping_schema = {
    n2: ([n1], [n3]),
    n3: ([n1], [n4]),
}
ccp = ControllerProtocol(controller, delay=0.25, distillation_schema=distillation_schema,
                         distillation_threshold=0.9, swapping_schema=swapping_schema)
controller.inject_protocol(ccp)
controller.install(s)

s.run()

de = []
for e in n4.registers:
    if n1 in e.nodes:
        de.append(e)

log.info("final distributed: {}: {}", len(de), de)
