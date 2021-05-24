
from .protocol import Protocol
from .event import Event
from .simulator import Simulator
from qns.schedular import simulator
import uuid


class Entity():
    '''
    ``Entity`` presents an entity in the network such as nodes, routers and links.
    It can also be used as a virtual entity such as a timer.

    One or more ``Protocol``'s should be injected into a entity to implement certain components and functions.

    :param name: the name of this entity. If ``name`` is ``None``, a random uuid4 will be used.
    '''

    def __init__(self, name = None):
        self.protocols = []
        self.sub_entities = []
        if name is None:
            self.name == uuid.uuid4()
        else:
            self.name = name

    def install(self, simulator: Simulator):
        '''
        ``install`` is called before ``simulator`` runs, it initial injected ``Protocol``'s.

        :param simulator: the simulator
        '''
        self.simulator = simulator
        for p in self.protocols:
            p.install(simulator)

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        '''
        ``handle`` is triggled by an ``Event``. It traverses all the protocols to handle this ``event``.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters 
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        for p in self.protocols:
            p.handle(simulator, msg, source, event)

    def call(self, simulator: Simulator, msg: object, source=None, event: Event = None, time_slice=None):
        '''
        ``call`` is an easy way to build an ``CallEvent`` and triggle itself's ``handle`` function in ``time_slice``.
        When ``time_slice`` is ``None``, the ``CallEvent`` will be called currently.

        ``call`` function is used when ``event`` is not important.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters 
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        callevent = CallEvent(self, simulator, msg, source, event)
        if time_slice is None:
            simulator.add_event(simulator.current_time_slice, callevent)
        else:
            simulator.add_event(time_slice, callevent)

    def inject_protocol(self, protocol):
        '''
        This function will inject one or more ``Protocol``'s into this entity.

        :param protocol: A ``Protocol`` or a list of it.
        '''
        if not hasattr(self, "protocols"):
            self.protocols = []
        if isinstance(protocol, list):
            for p in protocol:
                self.protocols.append(p)
        else:
            self.protocols.append(protocol)
    
    def add_subentity(self, entity):
        '''
        Add a sub entity into this subentity.

        :param entity: the sub entity
        '''
        self.sub_entities.append(entity)
    
    def get_subentity(self, name: str):
        '''
        retrive a sub entity by its name.

        :param str name: the name of this sub entity.
        :returns: the sub entity or ``None``
        '''
        for se in self.sub_entities:
            if se.name == name:
                return se
        return None



class CallEvent(Event):
    '''
    This event will call ``callee``'s ``handle`` function.

    :param callee: the event's receiver
    :param simulator: the simulator
    :param msg: anything, can be considered as the ``event``'s parameters 
    :param source: the entity that generated the ``event``
    :param event: the event 
    '''

    def __init__(self, callee, simulator: Simulator, msg: object, source=None, event: Event = None):
        self.simulator = simulator
        self.msg = msg
        self.source = source
        self.event = event
        self.callee = callee

    def run(self, simulator):
        '''
        This function call ``self.callee``'s ``handle`` function.
        '''
        self.callee.handle(self.simulator, self.msg, self.source, self.event)
