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

from qns.entity.cchannel.cchannel import ClassicChannel, RecvClassicPacket, ClassicPacket
from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel, RecvQubitPacket
from qns.entity.node.node import QNode
from qns.models.qubit.const import BASIS_X, BASIS_Z, \
    QUBIT_STATE_0, QUBIT_STATE_1, QUBIT_STATE_P, QUBIT_STATE_N
from qns.simulator.event import Event, func_to_event
from qns.simulator.simulator import Simulator
from qns.models.qubit import Qubit

from random import choice
import random
import numpy as np


class QubitWithError(Qubit):
    def transfer_error_model(self, length: float, **kwargs):
        lkm = length / 1000
        standand_lkm = 50.0
        theta = random.random() * lkm / standand_lkm * np.pi / 4
        operation = np.array([[np.cos(theta), - np.sin(theta)], [np.sin(theta), np.cos(theta)]], dtype=np.complex128)
        self.state.operate(operator=operation)


class BB84SendApp(Application):
    def __init__(self, dest: QNode, qchannel: QuantumChannel,
                 cchannel: ClassicChannel, send_rate=1000):
        super().__init__()
        self.dest = dest
        self.qchannel = qchannel
        self.cchannel = cchannel
        self.send_rate = send_rate

        self.count = 0
        self.qubit_list = {}
        self.basis_list = {}
        self.measure_list = {}

        self.succ_key_pool = {}
        self.fail_number = 0

    def install(self, node: QNode, simulator: Simulator):
        super().install(node, simulator)

        time_list = []
        time_list.append(simulator.ts)

        t = simulator.ts
        event = func_to_event(t, self.send_qubit)
        self._simulator.add_event(event)
        # while t <= simulator.te:
        #     time_list.append(t)
        #     t = t + simulator.time(sec = 1 / self.send_rate)

        #     event = func_to_event(t, self.send_qubit)
        #     self._simulator.add_event(event)

    def handle(self, node: QNode, event: Event):
        super().handle(node, event)
        if isinstance(event, RecvClassicPacket) and self.cchannel == event.cchannel:
            self.check_basis(event)

    def check_basis(self, event: RecvClassicPacket):
        packet = event.packet
        msg: dict = packet.get()
        id = msg.get("id")
        basis_dest = msg.get("basis")

        # qubit = self.qubit_list[id]
        basis_src = "Z" if (self.basis_list[id] == BASIS_Z).all() else "X"

        if basis_dest == basis_src:
            # log.info(f"[{self._simulator.current_time}] src check {id} basis succ")
            self.succ_key_pool[id] = self.measure_list[id]
        else:
            # log.info(f"[{self._simulator.current_time}] src check {id} basis fail")
            self.fail_number += 1

        packet = ClassicPacket(msg={"id": id, "basis": basis_src,
                               "ret": self.measure_list[id]}, src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)

    def send_qubit(self):

        # randomly generate a qubit
        state = choice([QUBIT_STATE_0, QUBIT_STATE_1,
                       QUBIT_STATE_P, QUBIT_STATE_N])
        qubit = QubitWithError(state=state)
        basis = BASIS_Z if (state == QUBIT_STATE_0).all() or (
            state == QUBIT_STATE_1).all() else BASIS_X
        # basis_msg = "Z" if (basis == BASIS_Z).all() else "X"

        ret = 0 if (state == QUBIT_STATE_0).all() or (
            state == QUBIT_STATE_P).all() else 1

        qubit.id = self.count
        self.count += 1
        self.qubit_list[qubit.id] = qubit
        self.basis_list[qubit.id] = basis
        self.measure_list[qubit.id] = ret

        # log.info(f"[{self._simulator.current_time}] send qubit {qubit.id},\
        #  basis: {basis_msg} , ret: {ret}")
        self.qchannel.send(qubit=qubit, next_hop=self.dest)

        t = self._simulator.current_time + \
            self._simulator.time(sec=1 / self.send_rate)
        event = func_to_event(t, self.send_qubit)
        self._simulator.add_event(event)


class BB84RecvApp(Application):
    def __init__(self, src: QNode, qchannel: QuantumChannel, cchannel: ClassicChannel):
        super().__init__()
        self.src = src
        self.qchannel = qchannel
        self.cchannel = cchannel

        self.qubit_list = {}
        self.basis_list = {}
        self.measure_list = {}

        self.succ_key_pool = {}
        self.fail_number = 0

    def handle(self, node: QNode, event: Event):
        if isinstance(event, RecvQubitPacket) and self.qchannel == event.qchannel:
            # receive a qubit
            return self.recv(event)
        elif isinstance(event, RecvClassicPacket) and self.cchannel == event.cchannel:
            return self.check_basis(event)
        return super().handle(node, event)

    def check_basis(self, event: RecvClassicPacket):
        packet = event.packet
        msg: dict = packet.get()
        id = msg.get("id")
        basis_src = msg.get("basis")

        # qubit = self.qubit_list[id]
        basis_dest = "Z" if (self.basis_list[id] == BASIS_Z).all() else "X"

        ret_dest = self.measure_list[id]
        ret_src = msg.get("ret")

        if basis_dest == basis_src and ret_dest == ret_src:
            # log.info(f"[{self._simulator.current_time}] dest check {id} basis succ")
            self.succ_key_pool[id] = self.measure_list[id]
        else:
            # log.info(f"[{self._simulator.current_time}] dest check {id} basis fail")
            self.fail_number += 1

    def recv(self, event: RecvQubitPacket):
        qubit: Qubit = event.qubit
        # randomly choose X,Z basis
        basis = choice([BASIS_Z, BASIS_X])
        basis_msg = "Z" if (basis == BASIS_Z).all() else "X"
        ret = qubit.measureZ() if (basis == BASIS_Z).all() else qubit.measureX()
        self.qubit_list[qubit.id] = qubit
        self.basis_list[qubit.id] = basis
        self.measure_list[qubit.id] = ret

        # log.info(f"[{self._simulator.current_time}] recv qubit {qubit.id}, \
        # basis: {basis_msg}, ret: {ret}")
        packet = ClassicPacket(
            msg={"id": qubit.id, "basis": basis_msg}, src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)
