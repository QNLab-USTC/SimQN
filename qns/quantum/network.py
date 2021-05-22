from qns.quantum.link import QuantumChannel
from .node import QuantumNode
from .entanglement import Entanglement
from qns.schedular import Entity, Simulator, Event


class QuantumNetwork(Entity):
    '''
    An entity that represents a quantum network.

    .. warning::
        It is deprecated.

    '''
    def __init__(self, quantum_nodes: int or QuantumNode = 10):
        if isinstance(quantum_nodes, int):
            self.quantum_nodes = [[QuantumNode()] * quantum_nodes]
        else:
            self.quantum_nodes = quantum_nodes

        self.links = []

    def install(self, simulator: Simulator):
        # inject myself into simulator
        Simulator.states["q"] = self
        self.simulator = simulator

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        pass

    def get_node(self, idx: int = None):
        if idx is not None:
            return [self.quantum_nodes[idx]]
        return self.quantum_nodes

    def add_node(self, node: QuantumNode):
        self.quantum_nodes.append(node)

    def del_node(self, node):
        self.quantum_nodes.remove(node)

    def add_link(self, link: QuantumChannel):
        self.links.append(QuantumChannel)

    def del_link(self, link: QuantumChannel):
        self.links.remove(link)
