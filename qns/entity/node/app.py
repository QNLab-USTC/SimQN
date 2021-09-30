from qns.simulator import Event
from qns.entity import QNode

class Application(object):
    """
    Application can be deployed on the `QNode`s
    """
    def __init__(self):
        pass

    def handle(self, node: QNode, event: Event):
        """
        process the event on the node.

        Args:
            node (QNode): the node that will handle this event
            evnet (Event): the event
        """
        pass