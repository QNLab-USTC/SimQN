from ..simulator import Simulator, Event, Time

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
            simulator (Simulator): the simulator
        '''
        if not self._is_installed:
            self._simulator = simulator
            self._is_installed = True
        
    def handle(self, event: Event) -> None:
        '''
        ``handle`` is triggled by an ``Event``.

        Args:
            event (Event): the event that triggles this entity.
        '''
        raise NotImplemented

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<entity {self.name}>"
        return super().__repr__()