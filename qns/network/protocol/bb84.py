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

import numpy as np
import random
import hashlib

from qns.utils.rnd import get_rand, get_choice


class QubitWithError(Qubit):
    def transfer_error_model(self, length: float, decoherence_rate: float = 0, **kwargs):
        lkm = length / 1000
        standand_lkm = 50.0
        theta = get_rand() * lkm / standand_lkm * np.pi / 4
        operation = np.array([[np.cos(theta), - np.sin(theta)], [np.sin(theta), np.cos(theta)]], dtype=np.complex128)
        self.state.operate(operator=operation)


class BB84SendApp(Application):
    def __init__(self, dest: QNode, qchannel: QuantumChannel,
                 cchannel: ClassicChannel, send_rate=1000,
                 min_length_for_post_processing=5000,
                 proportion_for_estimating_error=0.4, max_cascade_round=4,
                 cascade_alpha=0.73, cascade_beita=2,
                 init_lower_cascade_key_block_size=5,
                 init_upper_cascade_key_block_size=20,
                 security=0.05):
        """
        Args:
            dest: QNode.
            qchannel: QuantumChannel.
            cchannel: ClassicChannel.
            send_rate: the sending rate of qubit.
            min_length_for_post_processing: threshold to trigger post-processing.
            proportion_for_estimating_error: what proportion of bits are used for error estimating.
            max_cascade_round: how many rounds of cascade need to be executed.
            cascade_alpha: init_cascade_size = cascade_alpha / error_rate.
            cascade_beita: next_cascade_size = init_cascade_size * 2.
            init_lower_cascade_key_block_size: lower bound of init_cascade_size.
            init_upper_cascade_key_block_size: upper bound of init_cascade_size.
            security: parameter for privacy amplification.
        """
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

        # variable used in cascade and error estimate
        self.min_length_for_post_processing = min_length_for_post_processing
        self.proportion_for_estimating_error = proportion_for_estimating_error
        self.max_cascade_round = max_cascade_round
        self.cascade_alpha = cascade_alpha
        self.cascade_beita = cascade_beita
        self.init_lower_cascade_key_block_size = init_lower_cascade_key_block_size
        self.init_upper_cascade_key_block_size = init_upper_cascade_key_block_size

        self.using_post_processing = False
        self.cur_error_rate = 1e-6
        self.cur_cascade_round = 0
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        self.cascade_key = []

        # variable used in privacy amplification
        self.security = security

        self.bit_leak = 0
        self.successful_key = []

        self.add_handler(self.handleClassicPacket, [RecvClassicPacket], [self.cchannel])

    def install(self, node: QNode, simulator: Simulator):
        super().install(node, simulator)

        time_list = []
        time_list.append(simulator.ts)

        t = simulator.ts
        event = func_to_event(t, self.send_qubit, by=self)
        self._simulator.add_event(event)
        # while t <= simulator.te:
        #     time_list.append(t)
        #     t = t + simulator.time(sec = 1 / self.send_rate)

        #     event = func_to_event(t, self.send_qubit)
        #     self._simulator.add_event(event)

    def handleClassicPacket(self, node: QNode, event: Event):
        return self.check_basis(event) or self.recv_error_estimate_packet(event) or self.recv_cascade_ask_packet(event) or \
            self.recv_check_error_ask_packet(event) or self.recv_privacy_amplification_ask_packet(event)

    def check_basis(self, event: RecvClassicPacket):
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "check_basis":
            return False
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

        packet = ClassicPacket(msg={"packet_class": "check_basis", "id": id, "basis": basis_src,
                               "ret": self.measure_list[id]}, src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

    def send_qubit(self):

        # randomly generate a qubit
        state = get_choice([QUBIT_STATE_0, QUBIT_STATE_1,
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
        event = func_to_event(t, self.send_qubit, by=self)
        self._simulator.add_event(event)

    def recv_error_estimate_packet(self, event: RecvClassicPacket):
        """
        BB84SendApp recv error estimate packet,and send error_estimate_reply packet.

        Args:
            event:the error estimate packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "error_estimate":
            return False

        self.using_post_processing = True
        self.cur_error_rate = 1e-6
        self.cur_cascade_round = 0
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        self.cascade_key = []
        self.bit_leak = 0

        # get some recvapp error estimate info
        recv_app_bit_for_estimate = msg.get("bit_for_estimate")
        recv_app_bit_index_for_estimate = msg.get("bit_index_for_estimate")
        recv_app_bit_index_for_cascade = msg.get("bit_index_for_cascade")
        keys = list(self.succ_key_pool.keys())
        error_in_estimate = 0
        real_bit_length_for_estimate = 0
        real_bit_index_for_cascade = []

        # get cascade_key and count errors
        for i in keys:
            item_temp = self.succ_key_pool.pop(i)
            if i in recv_app_bit_index_for_estimate:
                # find a bit to estimate error
                bit_index = recv_app_bit_index_for_estimate.index(i)
                if item_temp == recv_app_bit_for_estimate[bit_index]:
                    real_bit_length_for_estimate += 1
                else:
                    real_bit_length_for_estimate += 1
                    error_in_estimate += 1
            elif i in recv_app_bit_index_for_cascade:
                # find a bit for cascade
                self.cascade_key.append(item_temp)
                real_bit_index_for_cascade.append(i)

        # error estimate and set key block size in round1
        self.cur_error_rate = error_in_estimate/real_bit_length_for_estimate

        if self.cur_error_rate <= (self.cascade_alpha/self.init_upper_cascade_key_block_size):
            # error rate is smaller than threshold
            self.cur_cascade_key_block_size = self.init_upper_cascade_key_block_size
        elif self.cur_error_rate >= (self.cascade_alpha/self.init_lower_cascade_key_block_size):
            self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        else:
            self.cur_cascade_key_block_size = int(self.cascade_alpha/self.cur_error_rate)

        self.cur_cascade_round = 1

        # send error_estimate_reply packet
        packet = ClassicPacket(msg={"packet_class": "error_estimate_reply",
                                    "error_rate": self.cur_error_rate,
                                    "real_bit_index_for_cascade": real_bit_index_for_cascade},
                               src=self._node,
                               dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

    def recv_cascade_ask_packet(self, event: RecvClassicPacket):
        """
        BB84SendApp recv cascade_ask packet,calculate the parity value of the corresponding block,and send cascade_reply packet.

        Args:
            event:the cascade_ask packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "cascade_ask":
            return False

        # get cascade_ask info
        parity_request = msg.get("parity_request")
        round_change_flag = msg.get("round_change_flag")
        shuffle_index = msg.get("shuffle_index")

        # cascade round change and shuffle cascade keys
        if round_change_flag is True and shuffle_index != []:
            self.cur_cascade_key_block_size = int(self.cur_cascade_key_block_size * self.cascade_beita)
            self.cur_cascade_round += 1
            self.cascade_key = [self.cascade_key[i] for i in shuffle_index]

        parity_answer = []
        for key_interval in parity_request:
            temp_parity = cascade_parity(self.cascade_key[key_interval[0]:key_interval[1]+1])
            parity_answer.append(temp_parity)

        self.bit_leak += len(parity_answer)

        # send cascade_reply packet
        packet = ClassicPacket(msg={"packet_class": "cascade_reply",
                                    "parity_answer": parity_answer},
                               src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

    def recv_check_error_ask_packet(self, event: RecvClassicPacket):
        """
        BB84SendApp recv check_error_ask packet,check error,and send check_error_reply packet.

        Args:
            event:the check_error_ask packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "check_error_ask":
            return False

        recv_hash_key = msg.get("hash_key")
        hash_key = hashlib.sha512(bytearray(self.cascade_key)).hexdigest()
        if hash_key != recv_hash_key:
            # cascade fail
            pa_flag = False
            packet = ClassicPacket(msg={"packet_class": "check_error_reply",
                                        "pa_flag": pa_flag},
                                   src=self._node, dest=self.dest)
        else:
            # cascade succeed
            pa_flag = True
            packet = ClassicPacket(msg={"packet_class": "check_error_reply",
                                        "pa_flag": pa_flag},
                                   src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

    def recv_privacy_amplification_ask_packet(self, event: RecvClassicPacket):
        """
        BB84SendApp recv privacy_amplification_ask packet,perform privacy amplification.

        Args:
            event:the privacy_amplification_ask packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "privacy_amplification_ask":
            return False
        pa_flag = msg.get("pa_flag")
        if pa_flag is True:
            # Alice's privacy amplification operation
            first_row = msg.get("first_row")
            first_col = msg.get("first_col")
            matrix_row = len(first_row)
            matrix_col = len(first_col)+1
            toeplitz_matrix = pa_generate_toeplitz_matrix(matrix_row, matrix_col, first_row, first_col)
            self.successful_key += list(pa_randomize_key(self.cascade_key, toeplitz_matrix))
            self.using_post_processing = False
            # validation output
        return True


class BB84RecvApp(Application):
    def __init__(self, src: QNode, qchannel: QuantumChannel, cchannel: ClassicChannel,
                 min_length_for_post_processing=5000,
                 proportion_for_estimating_error=0.4, max_cascade_round=4,
                 cascade_alpha=0.73, cascade_beita=2,
                 init_lower_cascade_key_block_size=5,
                 init_upper_cascade_key_block_size=20,
                 security=0.05):
        """
        Args:
            src: QNode.
            qchannel: QuantumChannel.
            cchannel: ClassicChannel.
            send_rate: the sending rate of qubit.
            min_length_for_post_processing: threshold to trigger post-processing.
            proportion_for_estimating_error: what proportion of bits are used for error estimating.
            max_cascade_round: how many rounds of cascade need to be executed.
            cascade_alpha: init_cascade_size = cascade_alpha / error_rate.
            cascade_beita: next_cascade_size = init_cascade_size * 2.
            init_lower_cascade_key_block_size: lower bound of init_cascade_size.
            init_upper_cascade_key_block_size: upper bound of init_cascade_size.
            security: parameter for privacy amplification.
        """
        super().__init__()
        self.src = src
        self.qchannel = qchannel
        self.cchannel = cchannel

        self.qubit_list = {}
        self.basis_list = {}
        self.measure_list = {}

        self.succ_key_pool = {}
        self.fail_number = 0

        # variable used in cascade and error estimate
        self.min_length_for_post_processing = min_length_for_post_processing
        self.proportion_for_estimating_error = proportion_for_estimating_error
        self.max_cascade_round = max_cascade_round
        self.cascade_alpha = cascade_alpha
        self.cascade_beita = cascade_beita
        self.init_lower_cascade_key_block_size = init_lower_cascade_key_block_size
        self.init_upper_cascade_key_block_size = init_upper_cascade_key_block_size

        self.using_post_processing = False
        self.cur_error_rate = 1e-6
        self.cur_cascade_round = 0
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        self.post_processing_key = {}
        self.cascade_key = []
        self.cascade_binary_set = []

        # variable used in privacy amplification
        self.security = security

        self.bit_leak = 0
        self.successful_key = []

        self.add_handler(self.handleQuantumPacket, [RecvQubitPacket], [self.qchannel])
        self.add_handler(self.handleClassicPacket, [RecvClassicPacket], [self.cchannel])

    def handleQuantumPacket(self, node: QNode, event: Event):
        return self.recv(event)

    def handleClassicPacket(self, node: QNode, event: Event):
        return self.check_basis(event) or self.recv_error_estimate_reply_packet(event) or \
            self.recv_cascade_reply_packet(event) or self.recv_check_error_reply_packet(event)

    def check_basis(self, event: RecvClassicPacket):
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "check_basis":
            return False
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

        if self.using_post_processing is False and len(self.succ_key_pool) >= self.min_length_for_post_processing:
            # enough raw key to start cascade
            self.send_error_estimate_packet()
        return True

    def recv(self, event: RecvQubitPacket):
        qubit: Qubit = event.qubit
        # randomly choose X,Z basis
        basis = get_choice([BASIS_Z, BASIS_X])
        basis_msg = "Z" if (basis == BASIS_Z).all() else "X"
        ret = qubit.measureZ() if (basis == BASIS_Z).all() else qubit.measureX()
        self.qubit_list[qubit.id] = qubit
        self.basis_list[qubit.id] = basis
        self.measure_list[qubit.id] = ret

        # log.info(f"[{self._simulator.current_time}] recv qubit {qubit.id}, \
        # basis: {basis_msg}, ret: {ret}")
        packet = ClassicPacket(
            msg={"packet_class": "check_basis", "id": qubit.id, "basis": basis_msg}, src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

    def send_error_estimate_packet(self):
        """
        BB84Recvapp send error estimate ask packet.
        """
        self.using_post_processing = True
        self.cur_cascade_round = 0
        self.cur_error_rate = 1e-6
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        self.cascade_key = []
        self.post_processing_key = {}
        self.cascade_binary_set = []
        self.bit_leak = 0

        # info to send
        bit_for_estimate = {}  # []
        bits_len_for_cascade = len(self.succ_key_pool)
        keys = list(self.succ_key_pool.keys())[0:bits_len_for_cascade]

        # remove uesd raw key and update cascade_key && bit_for_estimate
        for i in keys:
            item_temp = self.succ_key_pool.pop(i)
            if random.uniform(0, 1) < self.proportion_for_estimating_error:
                bit_for_estimate[i] = item_temp
            else:
                self.post_processing_key[i] = item_temp

        # send error_estimate packet
        packet = ClassicPacket(msg={"packet_class": "error_estimate",
                                    "bit_index_for_estimate": list(bit_for_estimate.keys()),
                                    "bit_for_estimate": list(bit_for_estimate.values()),
                                    "bit_index_for_cascade": list(self.post_processing_key.keys())},
                               src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

    def recv_error_estimate_reply_packet(self, event: RecvClassicPacket):
        """
        BB84RecvApp recv error_estimate_reply packet,perform the first round of cascade,send cascade_ask packet.

        Args:
            event:the error_estimate_reply packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "error_estimate_reply":
            return False

        # get error estimate info and set block size in round1
        self.cur_error_rate = msg.get("error_rate")
        if self.cur_error_rate <= (self.cascade_alpha/self.init_upper_cascade_key_block_size):
            # error rate is smaller than threshold
            self.cur_cascade_key_block_size = self.init_upper_cascade_key_block_size
        elif self.cur_error_rate >= (self.cascade_alpha/self.init_lower_cascade_key_block_size):
            # error rate is bigger than threshold
            self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        else:
            self.cur_cascade_key_block_size = int(self.cascade_alpha/self.cur_error_rate)

        self.cur_cascade_round = 1

        # remain real_bit_for_cascade
        real_bit_index_for_cascade = msg.get("real_bit_index_for_cascade")
        for i in list(self.post_processing_key.keys()):
            item_temp = self.post_processing_key.pop(i)
            if i in real_bit_index_for_cascade:
                self.cascade_key.append(item_temp)

        # start cascade round1,divide into top blocks of size self.keysize
        count_temp = 0
        last_index = len(self.cascade_key) - 1
        while count_temp <= last_index:
            end = count_temp + self.cur_cascade_key_block_size - 1
            if end <= last_index:
                self.cascade_binary_set.append((count_temp, end))
                count_temp = end + 1
            else:
                end = last_index
                self.cascade_binary_set.append((count_temp, end))
                break

        # send cascade_ask packet
        packet = ClassicPacket(msg={"packet_class": "cascade_ask",
                                    "parity_request": self.cascade_binary_set,
                                    "round_change_flag": False,
                                    "shuffle_index": []},
                               src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

        return True

    def recv_cascade_reply_packet(self, event: RecvClassicPacket):
        """
        BB84RecvApp recv cascade_reply packet,perform next round of cascade,and send cascade_ask packet.

        Args:
            event:the cascade_reply packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "cascade_reply":
            return False

        # get cascade_reply info
        parity_answer = msg.get("parity_answer")
        self.bit_leak += len(parity_answer)

        # update cascade binary set
        count_temp = 0
        # traverse all the blocks need to compare parity
        copy_cascade_binary_set = self.cascade_binary_set.copy()
        for key_interval in copy_cascade_binary_set:
            temp_parity = cascade_parity(self.cascade_key[key_interval[0]:key_interval[1]+1])
            if temp_parity == parity_answer[count_temp]:
                # this block have even errors,can not correct in this round
                self.cascade_binary_set.remove(key_interval)
            elif key_interval[0] != key_interval[1]:
                # binary alg
                self.cascade_binary_set.remove(key_interval)
                left_temp, right_temp = cascade_binary_divide(key_interval[0], key_interval[1])
                self.cascade_binary_set.append(left_temp)
                self.cascade_binary_set.append(right_temp)
            else:
                # find the odd error
                self.cascade_binary_set.remove(key_interval)
                self.cascade_key[key_interval[0]] = parity_answer[count_temp]

            count_temp += 1

        round_change_flag = False
        check_error_flag = False
        shuffle_index = []
        if len(self.cascade_binary_set) == 0:
            if self.cur_cascade_round == self.max_cascade_round:
                # update round info
                check_error_flag = True
                # check error
                hash_key = hashlib.sha512(bytearray(self.cascade_key)).hexdigest()
            else:
                # update round info
                round_change_flag = True
                self.cur_cascade_round += 1
                self.cur_cascade_key_block_size = int(self.cur_cascade_key_block_size * self.cascade_beita)
                # need shuffle
                shuffle_index = [i for i in range(len(self.cascade_key))]
                shuffle_index = cascade_key_shuffle(shuffle_index)
                self.cascade_key = [self.cascade_key[i] for i in shuffle_index]
                # divide into top blocks of size self.keysize
                count_temp = 0
                last_index = len(self.cascade_key) - 1
                while count_temp <= last_index:
                    end = count_temp + self.cur_cascade_key_block_size - 1
                    if end <= last_index:
                        self.cascade_binary_set.append((count_temp, end))
                        count_temp = end + 1
                    else:
                        end = last_index
                        self.cascade_binary_set.append((count_temp, end))
                        break

        # send cascade_ask packet,distinguish whether privacy amplification is required
        if check_error_flag is False:
            packet = ClassicPacket(msg={"packet_class": "cascade_ask",
                                        "parity_request": self.cascade_binary_set,
                                        "round_change_flag": round_change_flag,
                                        "shuffle_index": shuffle_index},
                                   src=self._node, dest=self.src)
        else:
            # check error
            packet = ClassicPacket(msg={"packet_class": "check_error_ask",
                                        "hash_key": hash_key},
                                   src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)
        return True

    def recv_check_error_reply_packet(self, event: RecvClassicPacket):
        """
        BB84RecvApp recv check_error_reply packet,perform privacy amplification,and send privacy_amplification_ask packet.

        Args:
            event:the check_error_reply packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "check_error_reply":
            return False
        pa_flag = msg.get("pa_flag")
        if pa_flag is True:
            # check error succeed,Bob's privacy amplification operation
            matrix_row = len(self.cascade_key)
            matrix_col = (1-self.security)*len(self.cascade_key)-self.bit_leak
            first_row = [random.randint(0, 1) for _ in range(matrix_row)]
            first_col = [random.randint(0, 1) for _ in range(int(matrix_col)-1)]
            toeplitz_matrix = pa_generate_toeplitz_matrix(matrix_row, matrix_col, first_row, first_col)
            self.successful_key += list(pa_randomize_key(self.cascade_key, toeplitz_matrix))
            packet = ClassicPacket(msg={"packet_class": "privacy_amplification_ask",
                                        "pa_flag": True,
                                        "first_row": first_row,
                                        "first_col": first_col},
                                   src=self._node, dest=self.src)
            self.using_post_processing = False
        else:
            # check error fail,drop
            first_row = []
            first_col = []
            packet = ClassicPacket(msg={"packet_class": "privacy_amplification_ask",
                                        "pa_flag": False,
                                        "first_row": first_row,
                                        "first_col": first_col},
                                   src=self._node, dest=self.src)
            self.using_post_processing = False
        self.cchannel.send(packet, next_hop=self.src)
        return True


def cascade_parity(target: list):
    """
        Calculate key block parity.

        Args:
            target:target key block.
    """
    count = sum(target)
    return count % 2


def cascade_binary_divide(begin: int, end: int):
    """
        Evenly divided the key block.

        Args:
            begin: key block begin index.
            end: key block end index.
    """
    len = end - begin + 1
    if len % 2 == 1:
        middle = int(len/2) + begin
    else:
        middle = int(len/2) + begin - 1
    return (begin, middle), (middle+1, end)


def cascade_key_shuffle(index: list):
    """
        Shuffle the index.

        Args:
            index: the index list.
    """
    np.random.shuffle(index)
    return index


def pa_generate_toeplitz_matrix(N: int, M: int, first_row: list, first_col: list):
    """
        Generate a Toeplitz matrix of size N x M using two given list of binary values.

        Args:
            N:col num of the Toeplitz matrix.
            M:row num of the Toeplitz matrix.
            first_row:first row of the Toeplitz matrix.
            first_col:first col of the Toeplitz matrix.
    """
    N = int(N)
    M = int(M)
    toeplitz_matrix = [[0] * N for _ in range(M)]
    for i in range(N):
        toeplitz_matrix[0][i] = first_row[i]
    for i in range(M-1):
        toeplitz_matrix[i+1][0] = first_col[i]
    for i in range(1, M):
        for j in range(1, N):
            toeplitz_matrix[i][j] = toeplitz_matrix[i-1][j-1]
    return toeplitz_matrix


def pa_randomize_key(original_key: list, toeplitz_matrix):
    """
        process the original key through the toeplitz matrix.

        Args:
            original_key: the original key.
            toeplitz_matrix: the toeplitz matrix.
    """
    return np.dot(toeplitz_matrix, original_key) % 2
