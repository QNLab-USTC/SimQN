from qns.simulator.ts import Time


def test_time():
    t1 = Time(1)
    t2 = Time(sec=1.1)
    t3 = Time()
    t4 = Time(1100000)

    print(t1.sec)

    assert (t1 == t1)
    assert (t2 >= t1)
    assert (t1 <= t2)
    assert (t1 < t2)
    assert (t3 < t1)
    assert (t2 == t4)


def print_msg(msg):
    print(msg)


def test_simulator_time():
    '''
    If we modify the default_accuracy of the simulator,
    check whether the accuracy of subsequent events will be automatically synchronized with the simulator
    without special modification.
    '''
    from qns.simulator.simulator import Simulator
    from qns.simulator.event import func_to_event
    s = Simulator(1, 10, 1000)
    print_event = func_to_event(Time(sec=1), print_msg, "hello world")
    print(print_event.t.accuracy)
    assert (print_event.t.accuracy == 1000)


