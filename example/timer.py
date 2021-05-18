from qns.schedular import Simulator
from qns.timer import Timer
from qns.log import log

s = Simulator(1,3600,1000)
log.install(s)
log.set_debug(True)


class TimerA(Timer):
    def run(self, simulator: Simulator):
        print(simulator.current_time)

ta = TimerA(2,3600,0.5, alloc_time = 60)
ta.install(s)
s.run()