from typing import Optional
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.entity.operator.event import OperateResponseEvent
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator
from qns.entity.operator import QuantumOperator, OperateRequestEvent
from qns.models.qubit import Qubit, H


def gate_z_and_measure(qubit: Qubit):
    H(qubit=qubit)
    result = qubit.measure()
    return result


def test_operator_sync():
    n1 = QNode("n1")
    o1 = QuantumOperator(name="o1", node=n1, gate=gate_z_and_measure)

    n1.add_operator(o1)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    qubit = Qubit()
    ret = o1.operate(qubit)
    assert(ret in [0, 1])

    s.run()


class RecvOperateApp(Application):
    def __init__(self):
        super().__init__()
        self.add_handler(self.OperateResponseEventhandler, [OperateResponseEvent], [])

    def OperateResponseEventhandler(self, node, event: Event) -> Optional[bool]:
        result = event.result
        assert(self._simulator.tc.sec == 0.5)
        assert(result in [0, 1])


def test_operator_async():
    n1 = QNode("n1")
    o1 = QuantumOperator(name="o1", node=n1, gate=gate_z_and_measure, delay=0.5)

    n1.add_operator(o1)
    a1 = RecvOperateApp()
    n1.add_apps(a1)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    qubit = Qubit()
    request = OperateRequestEvent(o1, qubits=[qubit], t=s.time(sec=0), by=n1)
    s.add_event(request)

    s.run()
