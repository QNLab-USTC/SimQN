import logging
from qns.simulator.simulator import Simulator
from qns.simulator.event import Event
import qns.utils.log as log

log.logger.setLevel(logging.DEBUG)


class TimerEvent(Event):
    def invoke(self) -> None:
        log.info(f"{self.name}: it is {self.t} seconds")

    def __repr__(self) -> str:
        return f"<{self.name}-{self.t}>"


def test_simulator_with_log():
    s = Simulator(0, 15, 1000)
    t = 0
    while t <= 12:
        e = TimerEvent(t=s.time(sec=t), name="t1")
        s.add_event(e)
        t += 0.5

    t = 5
    while t <= 20:
        e = TimerEvent(t=s.time(sec=t), name="t2")
        s.add_event(e)
        t += 1
    log.install(s)
    s.run()
