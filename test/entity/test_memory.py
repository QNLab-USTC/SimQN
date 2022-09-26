from typing import Optional
from qns.entity.memory.event import MemoryReadRequestEvent, MemoryReadResponseEvent, \
    MemoryWriteRequestEvent, MemoryWriteResponseEvent
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator
from qns.entity.memory.memory import QuantumMemory
from qns.models.qubit import Qubit
from qns.models.epr.werner import WernerStateEntanglement


def test_memory_sync_qubit():
    m = QuantumMemory("m1")
    n1 = QNode("n1")
    n1.add_memory(m)
    q1 = Qubit(name="test_qubit")

    s = Simulator(0, 10, 1000)
    n1.install(s)

    assert (m.write(q1))
    assert (m.read(key="test_qubit") is not None)


def test_memory_sync_qubit_limited():
    m = QuantumMemory("m1", capacity=5)
    n1 = QNode(name="n1")
    n1.add_memory(m)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    for i in range(5):
        q = Qubit(name="q"+str(i+1))
        assert (m.write(q))
        assert (m.count == i+1)

    q = Qubit(name="q5")
    assert (not m.write(q))
    assert (m.is_full())

    q = m.read(key="q4")
    assert (q is not None)
    assert (m.count == 4)
    assert (not m.is_full())
    q = Qubit(name="q6")
    assert (m.write(q))
    assert (m.is_full())
    assert (m._search(key="q6") == 3)


def test_memory_sync_epr():
    m = QuantumMemory(name="m1", capacity=10, decoherence_rate=0.2)
    n1 = QNode("n1")
    n1.add_memory(m)
    epr = WernerStateEntanglement(name="epr1", fidelity=1.0)
    s = Simulator(0, 1)
    n1.install(s)
    m.write(epr)
    s.run()
    after_epr = m.read("epr1")
    print("final fidelity", after_epr.fidelity)


def test_memory_async_qubit():
    class MemoryReadResponseApp(Application):
        def __init__(self):
            super().__init__()
            self.add_handler(self.MemoryReadhandler, [MemoryReadResponseEvent], [])
            self.add_handler(self.MemoryWritehandler, [MemoryWriteResponseEvent], [])

        def MemoryReadhandler(self, node, event: Event) -> Optional[bool]:
            print(1)
            result = event.result
            print("self._simulator.tc.sec: {}".format(self._simulator.tc))
            print("result: {}".format(result))
            assert (self._simulator.tc.sec == 1.5)
            assert (result is not None)

        def MemoryWritehandler(self, node, event: Event) -> Optional[bool]:
            result = event.result
            print("self._simulator.tc.sec: {}".format(self._simulator.tc))
            print("result: {}".format(result))
            assert (self._simulator.tc.sec == 0.5)
            assert (result)

    n1 = QNode("n1")
    app = MemoryReadResponseApp()
    n1.add_apps(app)

    m = QuantumMemory("m1", delay=0.5)
    n1.add_memory(m)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    q1 = Qubit(name="q1")
    write_request = MemoryWriteRequestEvent(memory=m, qubit=q1, t=s.time(sec=0), by=n1)
    read_request = MemoryReadRequestEvent(memory=m, key="q1", t=s.time(sec=1), by=n1)
    s.add_event(write_request)
    s.add_event(read_request)
    s.run()
