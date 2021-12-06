from qns.simulator.event import Event
from qns.simulator.ts import Time


class PrintEvent(Event):
    def invoke(self) -> None:
        print("event happened")


def test_event():

    te = PrintEvent(t=Time(sec=1), name="test event")
    print(te)

    te.invoke()
    assert(not te.is_canceled)
    te.cancel()
    assert(te.is_canceled)
