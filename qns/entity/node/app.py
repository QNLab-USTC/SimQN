from qns.simulator.simulator import Simulator
from qns.simulator import Event

class Application(object):
    """
    Application can be deployed on the `QNode`s
    """
    def __init__(self):
        pass

    def install(self, node: "QNode", simulator: Simulator):
        """
        install initial events for this QNode

        Args:
            node (QNode): the node that will handle this event
            simulator (Simulator): the simulator
        """
        pass

    def handle(self, node: "QNode", event: Event):
        """
        process the event on the node.

        Args:
            node (QNode): the node that will handle this event
            evnet (Event): the event
        """
        pass