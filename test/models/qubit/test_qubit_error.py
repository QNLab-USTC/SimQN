
from typing import Optional
import numpy as np
from qns.entity.memory.event import MemoryReadRequestEvent, MemoryReadResponseEvent, \
                                    MemoryWriteRequestEvent, MemoryWriteResponseEvent
from qns.entity.memory.memory import QuantumMemory
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.models.qubit.const import QUBIT_STATE_0, QUBIT_STATE_1
from qns.models.qubit.decoherence import DephaseMeasureErrorModel, DephaseOperateErrorModel, \
        DephaseStorageErrorModel, DepolarMeasureErrorModel, DepolarOperateErrorModel, DepolarStorageErrorModel
from qns.models.qubit.factory import QubitFactory
from qns.models.qubit.gate import X
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator


def test_qubit_measure_error():
    Qubit = QubitFactory(operate_decoherence_rate=0.2, measure_decoherence_rate=0.2)
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    c0 = q0.measure()
    ans = np.array([[1, 0], [0, 0]])
    assert ((ans == q0.state.rho).all())
    assert (c0 == 0)

    Qubit = QubitFactory(operate_decoherence_rate=0.2,
                         measure_decoherence_rate=0.2, measure_error_model=DepolarMeasureErrorModel)
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    q0.measure()

    Qubit = QubitFactory(operate_decoherence_rate=0.2,
                         measure_decoherence_rate=0.5, measure_error_model=DephaseMeasureErrorModel)
    q0 = Qubit(state=QUBIT_STATE_1, name="q0")
    q0.measure()


def test_qubit_operate_error():
    Qubit = QubitFactory(operate_decoherence_rate=0, operate_error_model=DepolarOperateErrorModel)
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    X(q0)

    Qubit = QubitFactory(operate_decoherence_rate=0.0000001, operate_error_model=DepolarOperateErrorModel)
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    X(q0)

    Qubit = QubitFactory(operate_decoherence_rate=0.2, operate_error_model=DephaseOperateErrorModel)
    q0 = Qubit(state=QUBIT_STATE_0, name="q0")
    X(q0)


def test_qubit_memory():
    Qubit = QubitFactory(store_error_model=DepolarStorageErrorModel)

    class MemoryReadResponseApp(Application):
        def __init__(self):
            super().__init__()
            self.add_handler(self.MemoryReadResponseHandler, [MemoryReadResponseEvent])
            self.add_handler(self.MemoryWriteResponseHandler, [MemoryWriteResponseEvent])

        def MemoryReadResponseHandler(self, node, event: Event) -> Optional[bool]:
            result = event.result
            print("self._simulator.tc.sec: {}".format(self._simulator.tc))
            print("result: {}".format(result))
            assert (self._simulator.tc.sec == 1.5)
            assert (result is not None)
            print(result.state)

        def MemoryWriteResponseHandler(self, node, event: Event) -> Optional[bool]:
            result = event.result
            print("self._simulator.tc.sec: {}".format(self._simulator.tc))
            print("result: {}".format(result))
            assert (self._simulator.tc.sec == 0.5)
            assert (result)

    n1 = QNode("n1")
    app = MemoryReadResponseApp()
    n1.add_apps(app)

    m = QuantumMemory("m1", delay=0.5, decoherence_rate=0.3)
    n1.add_memory(m)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    q1 = Qubit(name="q1")
    write_request = MemoryWriteRequestEvent(memory=m, qubit=q1, t=s.time(sec=0), by=n1)
    read_request = MemoryReadRequestEvent(memory=m, key="q1", t=s.time(sec=1), by=n1)
    s.add_event(write_request)
    s.add_event(read_request)
    s.run()


def test_qubit_memory_2():
    Qubit = QubitFactory(store_error_model=DephaseStorageErrorModel)

    class MemoryReadResponseApp(Application):
        def __init__(self):
            super().__init__()
            self.add_handler(self.MemoryReadResponseHandler, [MemoryReadResponseEvent])
            self.add_handler(self.MemoryWriteResponseHandler, [MemoryWriteResponseEvent])

        def MemoryReadResponseHandler(self, node, event: Event) -> Optional[bool]:
            result = event.result
            print("self._simulator.tc.sec: {}".format(self._simulator.tc))
            print("result: {}".format(result))
            assert (self._simulator.tc.sec == 1.5)
            assert (result is not None)
            print(result.state)

        def MemoryWriteResponseHandler(self, node, event: Event) -> Optional[bool]:
            result = event.result
            print("self._simulator.tc.sec: {}".format(self._simulator.tc))
            print("result: {}".format(result))
            assert (self._simulator.tc.sec == 0.5)
            assert (result)

    n1 = QNode("n1")
    app = MemoryReadResponseApp()
    n1.add_apps(app)

    m = QuantumMemory("m1", delay=0.5, decoherence_rate=0.3)
    n1.add_memory(m)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    q1 = Qubit(name="q1")
    write_request = MemoryWriteRequestEvent(memory=m, qubit=q1, t=s.time(sec=0), by=n1)
    read_request = MemoryReadRequestEvent(memory=m, key="q1", t=s.time(sec=1), by=n1)
    s.add_event(write_request)
    s.add_event(read_request)
    s.run()
