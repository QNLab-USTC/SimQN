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
from qns.simulator.ts import Time
from qns.simulator.event import Event
from qns.entity.cchannel.cchannel import ClassicChannel, ClassicPacket, RecvClassicPacket
import qns.utils.log as log
from qns.utils.rnd import get_rand


class RemoteClassicChannel(ClassicChannel):
    """
    ClassicChannel for cross-process links in MPI parallel simulation.

    Instead of adding events to the local event pool, events are tagged with
    ``dest_rank`` and pushed to the simulator's ``OutQ``.
    """

    def __init__(self, dest_rank: int, **kwargs):
        """
        Args:
            dest_rank: the MPI rank of the destination process
            **kwargs: same arguments as ``ClassicChannel``
        """
        super().__init__(**kwargs)
        self.dest_rank = dest_rank

    def send(self, packet: ClassicPacket, next_hop: QNode):
        from qns.entity.cchannel.cchannel import NextHopNotConnectionException

        if next_hop not in self.node_list:
            raise NextHopNotConnectionException

        if self.bandwidth != 0:
            if self._next_send_time <= self._simulator.current_time:
                send_time = self._simulator.current_time
            else:
                send_time = self._next_send_time

            if self.max_buffer_size != 0 and send_time > self._simulator.current_time\
               + self._simulator.time(sec=self.max_buffer_size / self.bandwidth):
                log.debug(f"cchannel {self}: drop packet {packet} due to overflow")
                return

            self._next_send_time = send_time + \
                self._simulator.time(sec=len(packet) / self.bandwidth)
        else:
            send_time = self._simulator.current_time

        if get_rand() < self.drop_rate:
            log.debug(f"cchannel {self}: drop packet {packet} due to drop rate")
            return

        recv_time = send_time + self._simulator.time(sec=self.delay_model.calculate())

        send_event = RecvClassicPacket(recv_time, name=None, by=self,
                                       cchannel=self, packet=packet, dest=next_hop)
        send_event.dest_rank = self.dest_rank
        self._simulator.OutQ.append(send_event)