from qns.simulator.simulator import Simulator
from qns.simulator.event import Event


class Entity(object):
    """
    This is the basic entity class, including memories, channels and nodes.
    """

    def __init__(self, name: str = None):
        """
        Args:
            name (str): the name of this entity
        """
        self.name = name
        self._is_installed = False
        self._simulator = None

    def install(self, simulator: Simulator) -> None:
        '''
        ``install`` is called before ``simulator`` runs to initialize or set initial events

        Args:
            simulator (qns.simulator.simulator.Simulator): the simulator
        '''
        if not self._is_installed:
            self._simulator = simulator
            self._is_installed = True

    def handle(self, event: Event) -> None:
        '''
        ``handle`` is called to process an receiving ``Event``.

        Args:
            event (qns.simulator.event.Event): the event that send to this entity
        '''
        raise NotImplementedError

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<entity {self.name}>"
        return super().__repr__()
