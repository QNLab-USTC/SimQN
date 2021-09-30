from typing import List
from qns.simulator import Event
from qns.entity import Entity
from qns.entity.node.app import Application

class QNode(Entity):
    """
    QNode is a quantum node in the quantum network
    """
    def __init__(self, name: str = None):
        """
        Args:
            name (str): the node's name
        """
        super().__init__(name=name)
        self.cchannels = []
        self.qchannels = []
        self.memories = []

        self.croute_table = []
        self.qroute_table = []
        self.apps: List[Application] = []

    def handle(self, event: Event) -> None:
        """
        This function will handle an `Event`. This event will be passed to every applications in apps list in order.

        Args:
            event (Event): the event that happens on this QNode
        """
        for app in self.apps:
            app.handle(self, event)
            

    def add_apps(self, app: Application):
        """
        Insert an Application into the app list.

        Args:
            app (Application): the inserting application.
        """
        self.apps.append(app)