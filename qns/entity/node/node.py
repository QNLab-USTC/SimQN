from typing import List
from qns.simulator import simulator
from qns.simulator import Event
from qns.entity import Entity
from qns.entity.node.app import Application

class QNode(Entity):
    """
    QNode is a quantum node in the quantum network
    """
    def __init__(self, name: str = None, apps: List[Application] = None):
        """
        Args:
            name (str): the node's name
            apps (List[Application]): the installing applications.
        """
        super().__init__(name=name)
        self.network = None
        self.cchannels = []
        self.qchannels = []
        self.memories = []

        self.croute_table = []
        self.qroute_table = []
        self.requests: List["Request"] = []
        if apps is None:
            self.apps: List[Application] = []
        else:
            self.apps: List[Application] = apps

    def install(self, simulator: simulator) -> None:
        super().install(simulator)
        # initize sub-entities
        for cchannel in self.cchannels:
            from qns.entity import ClassicChannel
            assert(isinstance(cchannel, ClassicChannel))
            cchannel.install(simulator)
        for qchannel in self.qchannels:
            from qns.entity import QuantumChannel
            assert(isinstance(qchannel, QuantumChannel))
            qchannel.install(simulator)
        for memory in self.memories:
            from qns.entity import QuantumMemory
            assert(isinstance(memory, QuantumMemory))
            memory.install(simulator)

        # initize applications
        for app in self.apps:
            app.install(self, simulator)


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

    def get_apps(self, app_type):
        """
        Get an Application that is `app_type`

        Args:
            app_type: the class of app_type
        """
        return [ app for app in self.apps if isinstance(app, app_type) ]
    
    def add_memory(self, memory):
        """
        Add a quantum memory in this QNode

        Args:
            memory (Memory): the quantum memory
        """
        memory.node = self
        self.memories.append(memory)

    def add_cchannel(self, cchannel):
        """
        Add a classic channel in this QNode

        Args:
            cchannel (ClassicChannel): the classic channel
        """
        cchannel.node_list.append(self)
        self.cchannels.append(cchannel)

    def get_cchannel(self, dst: "QNode"):
        """
        Get the classic channel that connects to the `dst`

        Args:
            dst (QNode): the destination
        """
        for cchannel in self.cchannels:
            if dst in cchannel.node_list and self in cchannel.node_list:
                return cchannel
        return None

    def add_qchannel(self, qchannel):
        """
        Add a quantum channel in this QNode

        Args:
            qchannel (QuantumChannel): the quantum channel
        """
        qchannel.node_list.append(self)
        self.qchannels.append(qchannel)

    def get_qchannel(self, dst: "QNode"):
        """
        Get the quantum channel that connects to the `dst`

        Args:
            dst (QNode): the destination
        """
        for qchannel in self.qchannels:
            if dst in qchannel.node_list and self in qchannel.node_list:
                return qchannel
        return None

    def add_request(self, request: "Request"):
        """
        add a request to this node

        Args:
            request (Request): the inserting request
        """
        self.requests.append(request)

    def clear_request(self):
        """
        clear all requests
        """
        self.requests.clear()

    def add_network(self, network):
        """
        add a network object to this node

        Args:
            network (qns.network.network.Network): the network object
        """
        self.network = network

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<node {self.name}>"
        return super().__repr__()