from .simulator import Simulator


class Protocol():
    '''
    Protocol defines a basic set of actions that an entity can do.
    ``install`` and ``handle`` are two functions that will be called to handle events

    :param Entity entity: the entity that this protocol injected
    '''
    def __init__(_self, entity):
        _self.entity = entity

    def install(_self, simulator: Simulator):
        '''
        ``install`` will be called before the simulator starts.
        It can be used to initialize or insert initial events.

        :param simulator: the simulator
        '''
        pass

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        '''
        ``handle`` is one of the callback functions that can be used to handle the triggered event.

        :param simulator: the simulator
        :param msg: anything, can be considered as the ``event``'s parameters 
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        pass
