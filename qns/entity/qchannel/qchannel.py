#    SimQN: a discrete-event simulator for the quantum networks
#    Copyright (C) 2021-2022 Lutong Chen, Jian Li, Kaiping Xue
#    University of Science and Technology of China, USTC.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Any, List, Optional, Union

from qns.entity.entity import Entity
from qns.entity.node.node import QNode
from qns.models.delay.constdelay import ConstantDelayModel
from qns.models.delay.delay import DelayModel
from qns.simulator.simulator import Simulator
from qns.simulator.ts import Time
from qns.simulator.event import Event
from qns.models.core.backend import QuantumModel
import qns.utils.log as log
from qns.utils.rnd import get_rand


class QuantumChannel(Entity):
    """
    QuantumChannel is the channel for transmitting qubit
    """
    def __init__(self, name: str = None, node_list: List[QNode] = [],
                 bandwidth: int = 0, delay: Union[float, DelayModel] = 0, drop_rate: float = 0,
                 max_buffer_size: int = 0, length: float = 0, decoherence_rate: Optional[float] = 0,
                 transfer_error_model_args: dict = {}):
        """
        Args:
            name (str): the name of this channel
            node_list (List[QNode]): a list of QNodes that it connects to
            bandwidth (int): the qubit per second on this channel. 0 represents unlimited
            delay (float): the time delay for transmitting a packet, or a ``DelayModel``
            drop_rate (float): the drop rate
            max_buffer_size (int): the max buffer size.
                If it is full, the next coming packet will be dropped. 0 represents unlimited.

            length (float): the length of this channel
            decoherence_rate: the decoherence rate that will pass to the transfer_error_model
            transfer_error_model_args (dict): the parameters that pass to the transfer_error_model
        """
        super().__init__(name=name)
        self.node_list = node_list.copy()
        self.bandwidth = bandwidth
        self.delay_model = delay if isinstance(delay, DelayModel) else ConstantDelayModel(delay=delay)
        self.drop_rate = drop_rate
        self.max_buffer_size = max_buffer_size
        self.length = length
        self.decoherence_rate = decoherence_rate
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

            if self.max_buffer_size != 0 and send_time > self._simulator.current_time\
               + self._simulator.time(sec=self.max_buffer_size / self.bandwidth):
                # buffer is overflow
                log.debug(f"qchannel {self}: drop qubit {qubit} due to overflow")
                return

            self._next_send_time = send_time + self._simulator.time(sec=1 / self.bandwidth)
        else:
            send_time = self._simulator.current_time

        # random drop
        if get_rand() < self.drop_rate:
            log.debug(f"qchannel {self}: drop qubit {qubit} due to drop rate")
            return

        #  add delay
        recv_time = send_time + self._simulator.time(sec=self.delay_model.calculate())

        # operation on the qubit
        qubit.transfer_error_model(self.length, self.decoherence_rate, **self.transfer_error_model_args)
        send_event = RecvQubitPacket(recv_time, name=None, by=self, qchannel=self,
                                     qubit=qubit, dest=next_hop)
        self._simulator.add_event(send_event)

    def __repr__(self) -> str:
        if self.name is not None:
            return "<qchannel "+self.name+">"
        return super().__repr__()


class NextHopNotConnectionException(Exception):
    pass


class RecvQubitPacket(Event):
    """
    The event for a QNode to receive a classic packet
    """
    def __init__(self, t: Optional[Time] = None, qchannel: QuantumChannel = None,
                 qubit: QuantumModel = None, dest: QNode = None, name: Optional[str] = None, by: Optional[Any] = None):
        super().__init__(t=t, name=name, by=by)
        self.qchannel = qchannel
        self.qubit = qubit
        self.dest = dest

    def invoke(self) -> None:
        self.dest.handle(self)
