from typing import List, Optional, Tuple, Union
from ..simulator import Simulator, Time, Event
from ..models import QuantumModel
from .entity import Entity
from .node import QNode

class OutOfMemoryException(Exception):
    pass

class QuantumMemory(Entity):
    """
    Quantum memory stores multiple `QuantumModel`
    """
    def __init__(self, name: str = None, node: QNode = None,capacity: int = 0):
        """
        Args:
            name (str): its name
            node (QNode): the quantum node that equips this memory
            capacity (int): the capacity of this quantum memory. 0 presents unlimited.
        """
        super().__init__(name=name)
        self.node = node
        self.capacity = capacity
        self.memory: List[Tuple[QuantumModel, Time]] = []

    def install(self, simulator: Simulator) -> None:
        return super().install(simulator)

    def read(self, key: Union[QuantumModel, str]) -> QuantumModel:
        """
        The API for reading a qubit from the memory

        Args:
            key (Union[QuantumModel, str]): the key. It can be a QuantumModel object, its name or the index number.
        """
        ret = None
        if isinstance(key, QuantumModel):
            for (q,t_store) in self.memory:
                if q == key:
                    ret = q
                    ret_t = t_store
                    break
        else:
            for (q,t_store) in self.memory:
                if hasattr(q, "name") and q.name is not None and q.name == key:
                    ret = q
                    ret_t = t_store
                    break
        if ret is None:
            return None
        self.memory.remove((ret, ret_t))
        t_now = self._simulator.current_time
        sec_diff = t_now.sec - ret_t.sec
        ret.storage_error_model(t = sec_diff)
        return ret

    def write(self, qm: QuantumModel) -> None:
        """
        The API for storing a qubit to the memory

        Args:
            qm (QuantumModel): the `QuantumModel`, could be a qubit or an entangled pair
        """
        if self.capacity > 0 and len(self.memory) >= self.capacity:
            raise OutOfMemoryException
        self.memory.append((qm, self._simulator.current_time))

    def handle(self, event: Event) -> None:
        return super().handle(event)