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

from typing import List, Optional, Union
from qns.entity.node.node import QNode
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.models.delay.constdelay import ConstantDelayModel
from qns.models.delay.delay import DelayModel


class QubitLossChannel(QuantumChannel):
    """
    QubitLossChannel is the channel that can loss qubits.

    The loss rate is: 1-(1-p_init)*10^{- attenuation_rate * length / 10}
    """
    def __init__(self, name: str = None, node_list: List[QNode] = [],
                 bandwidth: int = 0, delay: Union[float, DelayModel] = 0, p_init: float = 0, attenuation_rate: float = 0,
                 max_buffer_size: int = 0, length: float = 0, decoherence_rate: Optional[float] = 0,
                 transfer_error_model_args: dict = {}):
        """
        Args:
            name (str): the name of this channel
            node_list (List[QNode]): a list of QNodes that it connects to
            bandwidth (int): the qubit per second on this channel. 0 represents unlimited
            delay (float): the time delay for transmitting a packet, or a ``DelayModel``
            p_init: the probability of loss a qubit immediately
            attenuation_rate (float): the attenuation rate of the channel, in Db
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
        self.p_init = p_init
        self.attenuation_rate = attenuation_rate
        self.length = length
        self.drop_rate = 1 - (1-self.p_init)*10**(- self.attenuation_rate * self.length / 10)
        self.max_buffer_size = max_buffer_size
        self.decoherence_rate = decoherence_rate
        self.transfer_error_model_args = transfer_error_model_args
