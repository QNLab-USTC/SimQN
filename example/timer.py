from qns.schedular import Simulator
from qns.timer import Timer

s = Simulator(1,10,1000)

class TimerA(Timer):
    def run(self, simulator: Simulator):
        print(simulator.current_time)

ta = TimerA(2,5,0.5)
ta.install(s)
s.run()