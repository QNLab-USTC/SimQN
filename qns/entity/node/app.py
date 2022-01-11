from typing import Optional
from qns.simulator.simulator import Simulator
from qns.simulator import Event


class Application(object):
    """
    Application can be deployed on the quantum nodes.
    """
    def __init__(self):
        self._simulator = None
        self._node = None

    def install(self, node, simulator: Simulator):
        """
        install initial events for this QNode

        Args:
            node (QNode): the node that will handle this event
            simulator (Simulator): the simulator
        """
        self._simulator = simulator
        self._node = node

    def handle(self, node, event: Event) -> Optional[bool]:
        """
        process the event on the node.

        Args:
            node (QNode): the node that will handle this event
            event (Event): the event

        Return:
            skip (bool, None): if skip is True, further applications will not handle this event
        """
        pass

    def get_node(self):
        """
        get the node that runs this application

        Returns:
            the quantum node
        """
        return self._node

    def get_simulator(self):
        """
        get the simulator

        Returns:
            the simulator
        """
        return self._simulator
