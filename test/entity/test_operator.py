from typing import Optional

from numpy import isin
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.entity.operator.event import OperateResponseEvent
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator
from qns.entity.timer.timer import Timer
from qns.entity.operator import QuantumOperator, OperateRequestEvent
from qns.models.qubit import Qubit, H

def gate_z_and_measure(qubit: Qubit):
    H(qubit=qubit)
    result = qubit.measure()
    return result

def test_operator_sync():
    n1 = QNode("n1")
    o1 = QuantumOperator(name="o1", node = n1, gate = gate_z_and_measure)

    n1.add_operator(o1)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    def trigger_func():
        qubit = Qubit()
        ret = o1.operate(qubit)
        print(ret)

    t1 = Timer("t1", 0, 10, 1, trigger_func)
    t1.install(s)
    s.run()


class RecvOperateApp(Application):
    def handle(self, node, event: Event) -> Optional[bool]:
        if isinstance(event, OperateResponseEvent):
            result = event.result
            print(self._simulator.tc, result)

def test_operator_async():
    n1 = QNode("n1")
    o1 = QuantumOperator(name="o1", node = n1, gate = gate_z_and_measure, delay = 0.5)

    n1.add_operator(o1)
    a1 = RecvOperateApp()
    n1.add_apps(a1)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    def trigger_func():
        qubit = Qubit()
        request = OperateRequestEvent(o1, qubits=[qubit], t=s.tc)
        s.add_event(request)

    t1 = Timer("t1", 0, 10, 1, trigger_func)
    t1.install(s)
    s.run()