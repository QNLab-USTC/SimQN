from qns.simulator.simulator import Simulator
from qns.entity.timer.timer import Timer

s = Simulator(0, 10, 1000)


def trigger_func():
    print(s.current_time)


t1 = Timer("t1", 0, 10, 0.5, trigger_func)
t1.install(s)
s.run()
