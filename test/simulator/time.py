from qns.simulator.ts import Time

t1 = Time(1)
t2 = Time(sec=1.1)
t3 = Time()

assert(t1 == t1)
assert(t2 >= t1)
assert(t1 <= t2)
assert(t1 < t2)
assert(t3 < t1)
