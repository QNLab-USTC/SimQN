from qns.simulator.event import Event, func_to_event
from qns.simulator.ts import Time


class PrintEvent(Event):
    def invoke(self) -> None:
        print("event happened")


def test_event_normal():
    te = PrintEvent(t=Time(sec=1), name="test event")
    print(te)

    te.invoke()
    assert (not te.is_canceled)
    te.cancel()
    assert te.is_canceled


def Print():
    print("event happened")


def test_event_simple():
    te = func_to_event(t=Time(sec=1), name="test event", fn=Print)
    print(te)

    te.invoke()
