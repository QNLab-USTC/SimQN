from typing import Optional
from qns.entity.memory.event import MemoryReadRequestEvent, MemoryReadResponseEvent, \
                                    MemoryWriteRequestEvent, MemoryWriteResponseEvent
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator
from qns.entity.memory.memory import QuantumMemory
from qns.models.qubit import Qubit


def test_memory():
    m = QuantumMemory("m1")
    n1 = QNode("n1")
    n1.add_memory(m)
    q1 = Qubit(name="test_qubit")

    s = Simulator(0, 10, 1000)
    n1.install(s)

    assert(m.write(q1))
    assert(m.read(key="test_qubit") is not None)


def test_memory_async_read():
    class MemoryReadResponseApp(Application):
        def handle(self, node, event: Event) -> Optional[bool]:
            if isinstance(event, MemoryReadResponseEvent):
                result = event.result
                assert(self._simulator.tc.sec == 1.5)
                assert(result is not None)
            elif isinstance(event, MemoryWriteResponseEvent):
                result = event.result
                assert(self._simulator.tc.sec == 0.5)
                assert(result)

    n1 = QNode("n1")
    app = MemoryReadResponseApp()
    n1.add_apps(app)

    m = QuantumMemory("m1", delay=0.5)
    n1.add_memory(m)

    s = Simulator(0, 10, 1000)
    n1.install(s)

    q1 = Qubit(name="q1")
    write_reqeust = MemoryWriteRequestEvent(memory=m, qubit=q1, t=s.time(sec=0))
    read_request = MemoryReadRequestEvent(memory=m, key="q1", t=s.time(sec=1))
    s.add_event(write_reqeust)
    s.add_event(read_request)
    s.run()
