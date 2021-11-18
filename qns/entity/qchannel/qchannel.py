import random
from typing import List, Optional
from qns.entity import Entity
from qns.entity import QNode
from qns.simulator import Simulator, Time, Event
from qns.models import QuantumModel
from qns.utils.log import log

class QuantumChannel(Entity):
    """
    QuantumChannel is the channel for transmitting qubit
    """
    def __init__(self, name: str = None, node_list: List[QNode] = [], bandwidth: int = 0, delay: float = 0, drop_rate: float = 0, max_buffer_size: int = 0, length: float = 0, transfer_error_model_args: dict = {}):
        """
        Args:
            name (str): the name of this channel
            node_list (List[QNode]): a list of QNodes that it connects to
            bandwidth (int): the qubit per second on this channel. 0 represents unlimited
            delay (float): the time delay for transmitting a packet
            drop_rate (float): the drop rate
            max_buffer_size (int): the max buffer size. If it is full, the next coming packet will be dropped. 0 represents unlimited

            length (float): the length of this channel
            transfer_error_model_args (dict): the parameters that will pass to the transfer_error_model
        """
        super().__init__(name=name)
        self.node_list = node_list.copy()
        self.bandwidth = bandwidth
        self.delay = delay
        self.drop_rate = drop_rate
        self.max_buffer_size = max_buffer_size
        self.length = length
        self.transfer_error_model_args = transfer_error_model_args

    def install(self, simulator: Simulator) -> None:
        '''
        ``install`` is called before ``simulator`` runs to initialize or set initial events

        Args:
            simulator (Simulator): the simulator
        '''
        if not self._is_installed:
            self._simulator = simulator
            self._next_send_time = self._simulator.ts
            self._is_installed = True

    
    def send(self, qubit: QuantumModel, next_hop: QNode):
        """
        Send a qubit to the next_hop

        Args:
            qubit (QuantumModel): the transmitting qubit
            next_hop (QNode): the next hop QNode
        Raises:
            NextHopNotConnectionException: the next_hop is not connected to this channel
        """

        if next_hop not in self.node_list:
            raise NextHopNotConnectionException

        if self.bandwidth != 0:

            if self._next_send_time <= self._simulator.current_time:
                send_time = self._simulator.current_time
            else:
                send_time = self._next_send_time

            if self.max_buffer_size != 0 and send_time > self._simulator.current_time + self._simulator.time(sec = self.max_buffer_size / self.bandwidth):
                # buffer is overflow
                log.debug(f"qchannel {self}: drop qubit {qubit} due to overflow")
                return
            
            self._next_send_time = send_time + self._simulator.time(sec = 1 / self.bandwidth)
        else:
            send_time = self._simulator.current_time

        # random drop
        if random.random() < self.drop_rate:
            log.debug(f"qchannel {self}: drop qubit {qubit} due to drop rate")
            return

        #  add delay
        recv_time = send_time + self._simulator.time(sec = self.delay)

        # operation on the qubit
        qubit.transfer_error_model(self.length, **self.transfer_error_model_args)
        send_event = RecvQubitPacket(recv_time, name = None, qchannel= self, qubit = qubit, dest = next_hop)
        self._simulator.add_event(send_event)

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<qchannel {self.name}>"
        return super().__repr__()

class NextHopNotConnectionException(Exception):
    pass

class RecvQubitPacket(Event):
    """
    The event for a QNode to receive a classic packet
    """
    def __init__(self, t: Optional[Time] = None, name: Optional[str] = None, qchannel: QuantumChannel = None, qubit: QuantumModel = None, dest: QNode = None):
        super().__init__(t=t, name=name)
        self.qchannel = qchannel
        self.qubit = qubit
        self.dest = dest

    def invoke(self) -> None:
        self.dest.handle(self)