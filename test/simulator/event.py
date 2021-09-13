from qns import Event, Time

class TestEvent(Event):
    def invoke(self) -> None:
        print("event happened")

te = TestEvent(t = Time(sec=1), name ="test event")
print(te)

te.invoke()
assert(not te.is_canceled)
te.cancel()
assert(te.is_canceled)