from typing import Optional
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.network.protocol.node_process_delay import NodeProcessDelayApp
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator
from qns.simulator.ts import Time


class ProcessEvent(Event):
    def __init__(self, t: Optional[Time] = None, dest: QNode = None, name: Optional[str] = None):
        super().__init__(t, name)
        self.dest = dest

    def invoke(self) -> None:
        self.dest.handle(self)


class ProcessApp(Application):
    def __init__(self):
        super().__init__()

    def install(self, node, simulator: Simulator):
        super().install(node, simulator)

        for i in range(0, 10):
            t = simulator.time(sec=i)
            event = ProcessEvent(t=t, dest=self.get_node())
            self.get_simulator().add_event(event)

    def handle(self, node, event: Event) -> Optional[bool]:
        expected_recv_time = [i+0.5 for i in range(0, 10)]
        print(f"recv event at {event.t}")
        assert(event.t.sec in expected_recv_time)


def test_process_delay():
    n1 = QNode("n1")
    n1.add_apps(NodeProcessDelayApp(delay=0.5, delay_event_list=(ProcessEvent,)))
    n1.add_apps(ProcessApp())

    s = Simulator(0, 10)
    n1.install(s)

    s.run()
