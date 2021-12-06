from qns.entity.node.node import QNode
from qns.simulator.simulator import Simulator
from qns.entity.timer.timer import Timer
from qns.entity.memory.memory import QuantumMemory
from qns.models.qubit import Qubit


m = QuantumMemory("m1")
n1 = QNode("n1")
n1.add_memory(m)
q1 = Qubit()

s = Simulator(0, 10, 1000)
n1.install(s)


def trigger_func():
    m.write(q1)
    q2 = m.read(q1)
    print(q2)


t1 = Timer("t1", 0, 10, 0.5, trigger_func)
t1.install(s)
s.run()
