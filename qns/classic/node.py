from qns.schedular import Simulator, Protocol
from qns.topo import Node
from qns.log import log
from .message import Message


class ClassicNode(Node):
    '''
    This is a Classic Node class

    :param str name: the name of this network node.
    :param classic_links: attached classic link (ClassicLink)
    '''

    def __init__(self, name=None):
        super().__init__(name)
        self.classic_links = []

    def __repr__(self):
        return "<classic node " + self.name+">"


class ClassicSendProtocol(Protocol):
    '''
    This is a Protocol that enables a classic node or a quantum node to send a classic ``Message``

    :param qns.topo.basic.Node entity: the entity that will inject this protocol
    '''
    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        _self.simulator = simulator

    def handle(_self, simulator: Simulator, msg: Message, source=None, event=None):
        '''
        When this handle function is called, the ``msg`` will be send on the link ``msg.link``.

        :param simulator: the simulator
        :param Message msg: The classic message to be sent
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        self = _self.entity
        link = msg.link

        if link not in self.classic_links:
            log.debug("link {} is not attached on {}", link, self)

        log.debug("{} send {} on {}", self, msg, link)
        link.call(simulator, msg, source=self, event=event)


class ClassicRecvProtocol(Protocol):
    '''
    This is a Protocol that enables a classic node or a quantum node to receive a classic message.
    Then, the ``entity`` will print this message.

    This Protocol can be overrided to implement other functions.

    :param qns.topo.basic.Node entity: the entity that will inject this protocol
    '''
    def __init__(_self, entity):
        super().__init__(entity)

    def install(_self, simulator: Simulator):
        _self.simulator = simulator

    def handle(_self, simulator: Simulator, msg: object, source=None, event=None):
        '''
        When this handle function is called, the ``entity`` will print the received ``msg``.

        :param simulator: the simulator
        :param Message msg: The classic message to be sent
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        self = _self.entity

        log.debug("{} recv {} from {}",
                  self, msg, source)

# ClassicSwitchProtocol
# forwarding table = {outnode1: outlink1, outnode2: outlink2}
# buffer_size maximun buffer size
# delay delay time in seconde


class ClassicSwitchProtocol(Protocol):
    '''
    This protocol enables a node to be a classic switcher.
    When the node receive a message, it will look up the ``forwarding`` table and decide which link will be used to forward this message.
    The ``forwarding`` table has the following format:

        ``{outnode1: outlink1, outnode2: outlink2 ...}``

    :param qns.topo.basic.Node entity: the entity that will inject this protocol
    :param forwarding: a ``dict`` that indicates the target node and its next hop link.
    :param delay: the delay time of handling each message in second.
    '''
    def __init__(_self, entity, forwarding={}, delay=0, buffer_size=None):
        super().__init__(entity)
        _self.delay = delay
        _self.forwarding = forwarding
        _self.buffer_size = buffer_size

    def install(_self, simulator: Simulator):
        _self.simulator = simulator
        _self.delay_time_slice = simulator.to_time_slice(_self.delay)

    def handle(_self, simulator: Simulator, msg: Message, source=None, event=None):
        '''
        When this handle function is called, the ``msg`` will be forwarded by the ``forwarding`` table.

        :param simulator: the simulator
        :param Message msg: The classic message to be sent
        :param source: the entity that generated the ``event``
        :param event: the event 
        '''
        self = _self.entity
        try:
            link = _self.forwarding[msg.to_node]
        except KeyError:
            log.debug("{} can not forward to node {} ", self, source)
            return
        log.debug("{} send {} on {}", self, msg, link)
        link.call(simulator, msg, source=self, event=event,
                  time_slice=simulator.current_time_slice + _self.delay_time_slice)
