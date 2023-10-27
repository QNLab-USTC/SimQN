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

        # variable used in cascade
        self.using_cascade = False
        self.cascade_round = 0
        self.current_error_rate = 0
        self.cascade_key = []
        self.coordination_key_pool = []
        self.cascade_key_block_size = 20
        self.bit_leak = 0
        
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
        return self.check_basis(event) or self.recv_error_estimate_packet(event) or self.recv_cascade_ask_packet(event)

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

        packet = ClassicPacket(msg={"packet_class": "check_basis","id": id, "basis": basis_src,
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
        # BB84SendApp recv error estimate packet
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "error_estimate":
            return False
        
        self.using_cascade = True
        self.current_error_rate = 0
        self.cascade_round = 0
        self.cascade_key = []
        self.cascade_key_block_size = 20
        self.bit_leak = 0

        # get some recvapp error estimate info
        bits_len_for_cascade = msg.get("bits_len_for_cascade")
        bits_len_for_estimate = msg.get("bits_len_for_estimate")
        recv_app_bits_for_estimate = msg.get("bit_for_estimate")
        keys = list(self.succ_key_pool.keys())[0:bits_len_for_cascade]
        error_in_estimate = 0
        bit_for_estimate = []
        count_temp = 0

        # remove uesd raw key
        for i in keys:
            item_temp = self.succ_key_pool.pop(i)
            count_temp += 1
            if count_temp <= bits_len_for_estimate:
                bit_for_estimate.append(item_temp)
            else :
                self.cascade_key.append(item_temp)
        
        # count errors
        for i in range(len(bit_for_estimate)):
            if bit_for_estimate[i] != recv_app_bits_for_estimate[i]:
                error_in_estimate += 1
        
        # error estimate and set key block size in round1
        self.current_error_rate = error_in_estimate/bits_len_for_estimate
        print("error rate is {}".format(self.current_error_rate))
        if self.current_error_rate >= 0.0365:
            self.cascade_key_block_size = int(0.73/self.current_error_rate)
        self.cascade_round = 1
        
        # send error_estimate_reply packet
        packet = ClassicPacket(msg={"packet_class": "error_estimate_reply",
                                    "error_rate": self.current_error_rate}, 
                                    src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True
    
    def recv_cascade_ask_packet(self, event: RecvClassicPacket):
        # BB84SendApp recv cascade_ask packet
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "cascade_ask":
            return False
        
        # get cascade_ask info
        parity_request = msg.get("parity_request")
        round_change_flag = msg.get("round_change_flag")
        shuffle_index = msg.get("shuffle_index")
        privacy_flag = msg.get("privacy_flag")

        # cascade process end and privacy amplification
        if privacy_flag == True:
            # To Do
            print("it is time to privacy amplification!")
            return True
        
        # cascade round change and shuffle cascade keys
        elif round_change_flag == True and shuffle_index != []:
            self.cascade_key_block_size *= 2
            self.cascade_round += 1
            self.cascade_key = [self.cascade_key[i] for i in shuffle_index]
        
        parity_answer = []
        for key_interval in parity_request:
            temp_parity = cascade_parity(self.cascade_key[key_interval[0]:key_interval[1]+1])
            parity_answer.append(temp_parity)

        self.bit_leak += len(parity_answer)
        print(parity_answer)

        # send cascade_reply packet
        packet = ClassicPacket(msg={"packet_class": "cascade_reply",
                                    "parity_answer": parity_answer}, 
                                    src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

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

        # variable used in cascade
        self.using_cascade = False
        self.cascade_round = 0
        self.current_error_rate = 0
        self.cascade_key = []
        self.coordination_key_pool = []
        self.cascade_key_block_size = 20
        self.cascade_binary_set = []
        self.bit_leak = 0
        
        self.add_handler(self.handleQuantumPacket, [RecvQubitPacket], [self.qchannel])
        self.add_handler(self.handleClassicPacket, [RecvClassicPacket], [self.cchannel])

    def handleQuantumPacket(self, node: QNode, event: Event):
        return self.recv(event)

    def handleClassicPacket(self, node: QNode, event: Event):
        return self.check_basis(event) or self.recv_error_estimate_reply_packet(event) or self.recv_cascade_reply_packet(event)

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
        
        if self.using_cascade is False and len(self.succ_key_pool) >= 5000:
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
            msg={"packet_class": "check_basis","id": qubit.id, "basis": basis_msg}, src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

    def send_error_estimate_packet(self):
        # BB84RecvApp use some raw bits and estimate
        self.cascade_key = []
        self.cascade_binary_set = []
        self.using_cascade = True
        self.cascade_round = 0
        self.current_error_rate = 0
        self.cascade_key_block_size = 20
        self.bit_leak = 0

        # info to send
        count_temp = 0        
        bit_for_estimate = []
        bits_len_for_estimate = 2000
        bits_len_for_cascade = len(self.succ_key_pool)  
        keys = list(self.succ_key_pool.keys())[0:bits_len_for_cascade]

        # remove uesd raw key and update cascade_key && bit_for_estimate
        for i in keys:
            item_temp = self.succ_key_pool.pop(i)
            count_temp += 1
            if count_temp <= bits_len_for_estimate:
                bit_for_estimate.append(item_temp)
            else :
                self.cascade_key.append(item_temp)
        
        # send error_estimate packet
        packet = ClassicPacket(msg={"packet_class": "error_estimate", 
                                    "bit_for_estimate": bit_for_estimate,
                                    "bits_len_for_cascade": bits_len_for_cascade, 
                                    "bits_len_for_estimate": bits_len_for_estimate}, 
                                    src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

    def recv_error_estimate_reply_packet(self, event: RecvClassicPacket):
        # BB84RecvApp recv error estimate reply packet
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != "error_estimate_reply":
            return False
        
        # get error estimate info and set block size in round1
        self.current_error_rate = msg.get("error_rate")
        if self.current_error_rate >= 0.0365:
            self.cascade_key_block_size = int(0.73/self.current_error_rate)
        self.cascade_round = 1

        # start cascade round1,divide into top blocks of size self.keysize 
        count_temp = 0
        last_index = len(self.cascade_key) - 1
        while count_temp <= last_index:
            end = count_temp + self.cascade_key_block_size - 1
            if end <= last_index:
                self.cascade_binary_set.append((count_temp,end))
                count_temp = end + 1
            else:
                end = last_index
                self.cascade_binary_set.append((count_temp,end))
                break

        # send cascade_ask packet
        packet = ClassicPacket(msg={"packet_class": "cascade_ask", 
                                    "parity_request": self.cascade_binary_set,
                                    "round_change_flag": False, 
                                    "shuffle_index" : [],
                                    "privacy_flag": False}, 
                               src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

        return True
    
    def recv_cascade_reply_packet(self, event: RecvClassicPacket):
        # BB84RecvApp recv cascade_reply packet
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
                left_temp,right_temp = cascade_binary_divide(key_interval[0],key_interval[1])
                self.cascade_binary_set.append(left_temp)
                self.cascade_binary_set.append(right_temp)
            else :
                # find the odd error
                self.cascade_binary_set.remove(key_interval)
                self.cascade_key[key_interval[0]] = parity_answer[count_temp]
                
            count_temp += 1
        
        round_change_flag = False
        privacy_flag = False
        shuffle_index = []
        if len(self.cascade_binary_set) == 0:
            if self.cascade_round == 4:
                # update round info 
                # To Do
                privacy_flag = True
            else :
                # update round info    
                round_change_flag = True
                self.cascade_round += 1
                self.cascade_key_block_size *= 2
                # need shuffle
                shuffle_index = [i for i in range(len(self.cascade_key))]
                shuffle_index = cascade_key_shuffle(shuffle_index)
                self.cascade_key = [self.cascade_key[i] for i in shuffle_index]
                # divide into top blocks of size self.keysize 
                count_temp = 0
                last_index = len(self.cascade_key) - 1
                while count_temp <= last_index:
                    end = count_temp + self.cascade_key_block_size - 1
                    if end <= last_index:
                        self.cascade_binary_set.append((count_temp,end))
                        count_temp = end + 1
                    else:
                        end = last_index
                        self.cascade_binary_set.append((count_temp,end))
                        break
        
        print(self.cascade_binary_set)        
        # send cascade_ask packet
        packet = ClassicPacket(msg={"packet_class": "cascade_ask", 
                                    "parity_request": self.cascade_binary_set,
                                    "round_change_flag": round_change_flag, 
                                    "shuffle_index" : shuffle_index,
                                    "privacy_flag": privacy_flag}, 
                               src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)
        return True

def cascade_parity(target:list):
    # calculate parity
    count = sum(target)
    return count % 2

def cascade_binary_divide(begin: int,end: int):
    # binnary devide
    len = end - begin + 1
    if len % 2 == 1:
        middle = int(len/2) + begin  
    else :
        middle = int(len/2) + begin - 1
    return (begin,middle),(middle+1,end)

def cascade_key_shuffle(index:list):
    # shuffle the index
    np.random.shuffle(index)
    return index