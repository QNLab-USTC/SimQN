from qns.simulator.ts import Time


def test_time():
    t1 = Time(1)
    t2 = Time(sec=1.1)
    t3 = Time()
    t4 = Time(1100000)

    print(t1.sec)

    assert(t1 == t1)
    assert(t2 >= t1)
    assert(t1 <= t2)
    assert(t1 < t2)
    assert(t3 < t1)
    assert(t2 == t4)
