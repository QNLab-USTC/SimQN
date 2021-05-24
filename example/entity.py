from qns.schedular import Simulator, Event, Entity


class TestClockEntity(Entity):
    def __init__(self, start_time, end_time, step_time, name = None):
        super().__init__(name)
        self.step_time = step_time
        self.start_time = start_time
        self.end_time = end_time

    def install(self, simulator: Simulator):
        self.step_time_slice = simulator.to_time_slice(self.step_time)
        self.start_time_slice = simulator.to_time_slice(self.start_time)
        self.end_time_slice = simulator.to_time_slice(self.end_time)

        class TextClockEvent(Event):
            def run(self, simulator: Simulator):
                print(simulator.current_time)

        for i in range(self.start_time_slice, self.end_time_slice, self.step_time_slice):
            simulator.add_event(i, TextClockEvent())


s = Simulator(0, 100, 1000000)
clock = TestClockEntity(20, 70, 5)
clock.install(s)
s.run()
