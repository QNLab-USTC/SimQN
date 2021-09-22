from qns import Event, Time, Simulator
from qns.entity import Timer



s = Simulator(0, 10, 1000)

def triggle_func():
    print(s.current_time)

t1 = Timer("t1", 0, 10, 0.5, triggle_func)

t1.install(s)
s.run()