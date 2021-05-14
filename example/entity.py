from qns.schedular import Simulator, Event, Entity

class TestClockEntity(Entity):
    def handle(self, simulator: Simulator):
        print("current time:", simulator.to_time(simulator.current_time_slice), "s")

s = Simulator(0, 1, 1000)
clock = TestClockEntity()
clock.install(s)
s.run()