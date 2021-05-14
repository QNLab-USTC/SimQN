from qns.schedular import Simulator, Event

class TestEvent(Event):
    def run(self, simulator: Simulator):

        id = simulator.states.get("id", 0)
        simulator.states["id"] = id + 1
        print("event", id, "started at", self.start_time, "ms")

        ne = TestEvent()
        current_time_slice = simulator.current_time_slice
        new_time_slice = current_time_slice + simulator.to_time_slice(5.0)
        simulator.add_event(new_time_slice, ne)
        print("event", id, "produced new event at", simulator.to_time(new_time_slice), "ms")

events_list = [
    (20.0, TestEvent()),
    (30.0, TestEvent())
]

s = Simulator(0, 100.0, 10, events_list= events_list)
s.run()
