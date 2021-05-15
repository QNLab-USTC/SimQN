from qns.schedular import Entity, Simulator, Event


class Node(Entity):
    def install(self, simulator: Simulator):
        pass

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        pass


class Channel(Entity):
    def install(self, simulator: Simulator):
        pass

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        pass
