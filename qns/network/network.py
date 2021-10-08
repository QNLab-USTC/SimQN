from typing import Callable, List, Optional, Sequence, Tuple
from qns.entity import QNode, QuantumChannel, QuantumMemory, ClassicChannel
from qns.network.topology import Topology
from qns.network.route import RouteImpl, DijkstraRouteAlgorithm

class QuantumNetwork(object):
    """
    QuantumNetwork includes several quantum nodes, channels and a special topology
    """

    def __init__(self, topo: Optional[Topology] = None, route: Optional[RouteImpl] = None):
        """
        Args:
            topo: a `Topology` class. If topo is not None, a special quantum topology is built.
            route: the route implement. If route is None, the dijkstra algorithm will be used
        """
        self.cchannels: List[ClassicChannel] = []
        if topo is None:
            self.nodes = []
            self.qchannels = []
        else:
            self.nodes, self.qchannels = topo.build()
            for n in self.nodes:
                n.network = self

        if route is None:
            self.route: RouteImpl = DijkstraRouteAlgorithm()
        else:
            self.route: RouteImpl = route
        
    def add_node(self, node: QNode):
        """
        add a QNode into this netowrk.

        Args:
            node (QNode): the inserting node
        """
        self.nodes.append(node)
        node.network = self

    def get_node(self, name: str):
        """
        get the QNode by its name

        Args:
            name (str): its name
        Returns:
            the QNode
        """
        for n in self.nodes:
            if n.name == name:
                return n
        return None

    def add_qchannel(self, qchannel: QuantumChannel):
        """
        add a QuantumChannel into this netowrk.

        Args:
            qchannel (QuantumChannel): the inserting QuantumChannel
        """
        self.qchannels.append(qchannel)

    def get_qchannel(self, name: str):
        """
        get the QuantumChannel by its name

        Args:
            name (str): its name
        Returns:
            the QuantumChannel
        """
        for n in self.qchannels:
            if n.name == name:
                return n
        return None

    def add_cchannel(self, cchannel: ClassicChannel):
        """
        add a ClassicChannel into this netowrk.

        Args:
            cchannel (ClassicChannel): the inserting ClassicChannel
        """
        self.cchannels.append(cchannel)
    
    def get_cchannel(self, name: str):
        """
        get the ClassicChannel by its name

        Args:
            name (str): its name
        Returns:
            the ClassicChannel
        """
        for n in self.cchannels:
            if n.name == name:
                return n
        return None

    def add_memories(self, capacity: int = 0, store_error_model_args: dict = {}):
        """
        Add quantum memories to every nodes in this network

        Args:
            capacity (int): the capacity of the quantum memory
            store_error_model_args: the arguments for store_error_model
        """
        for idx, n in enumerate(self.nodes):
            m = QuantumMemory(name=f"m{idx}", node = n, capacity = capacity, store_error_model_args = store_error_model_args)
            n.add_memory(m)

    def build_route(self):
        """
        build static route tables for each nodes
        """
        self.route.build(self.nodes, self.qchannels)
    
    def query_route(self, src: QNode, dest: QNode) -> List[Tuple[float, QNode, List[QNode]]]:
        """
        query the metric, nexthop and the path

        Args:
            src: the source node
            dest: the destination node
        
        Returns:
            A list of route paths. The result should be sortted by the perority.
            The element is a tuple containing: metric, the next-hop and the whole path.
        """
        return self.route.query(src, dest)