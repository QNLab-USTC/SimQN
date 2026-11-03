from qns.entity.cchannel.cchannel import ClassicChannel, RecvClassicPacket, ClassicPacket
from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel, RecvQubitPacket
from qns.entity.node.node import QNode
from qns.models.qubit.const import BASIS_X, BASIS_Z, \
    QUBIT_STATE_0, QUBIT_STATE_1, QUBIT_STATE_P, QUBIT_STATE_N
from qns.simulator.event import Event, func_to_event
from qns.simulator.simulator import Simulator
from qns.models.qubit import Qubit
from qns.utils.rnd import get_rand, get_choice

import hashlib
import numpy as np

PACKET_CHECK_BASIS: int = 0  # Basis check packet
PACKET_ERROR_ESTIMATE: int = 1  # Error rate estimation packet
PACKET_CASCADE: int = 2  # Cascade packet
PACKET_CHECK_ERROR: int = 3  # Error verification packet
PACKET_PRIVACY_AMPLIFICATION: int = 4  # Privacy amplification packet

KEY_BLOCK_SIZE: int = 512  # Key block size


def cascade_parity(target: list):
    """
        Calculate the parity of a key block.

        Args:
            target: Key block to calculate.
        Returns:
            int: Parity value.
    """
    count = sum(target)
    return count % 2


def cascade_binary_divide(begin: int, end: int):
    """
        Binary divide key block indices.

        Args:
            begin: Start index of the key block.
            end: End index of the key block.
        Returns:
            tuple: Divided key block indices.
    """
    len = end - begin + 1
    if len % 2 == 1:
        middle = int(len/2) + begin
    else:
        middle = int(len/2) + begin - 1
    return (begin, middle), (middle+1, end)


def cascade_key_shuffle(index: list):
    """
        Randomly shuffle key block indices.

        Args:
            index: List of key block indices.
        Returns:
            list: Shuffled key block indices.
    """
    np.random.shuffle(index)
    return index


def pa_generate_toeplitz_matrix(N: int, M: int, first_row: list, first_col: list):
    """
        Generate a Toeplitz matrix of size N x M.

        Args:
            N: Number of columns in the Toeplitz matrix.
            M: Number of rows in the Toeplitz matrix.
            first_row: First row of the Toeplitz matrix.
            first_col: First column of the Toeplitz matrix.
        Returns:
            list: Toeplitz matrix of size N x M.
    """
    N = int(N)
    M = int(M)
    toeplitz_matrix = [[0] * N for _ in range(M)]
    # Fill the first row and first column of the Toeplitz matrix
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
        Perform privacy amplification using a Toeplitz matrix.

        Args:
            original_key: Original key.
            toeplitz_matrix: Toeplitz matrix.
        Returns:
            np_array: Key after privacy amplification.
    """
    return np.dot(toeplitz_matrix, original_key) % 2


class QubitWithError(Qubit):
    def transfer_error_model(self, length: float, decoherence_rate: float = 0, **kwargs):
        """
        Noise model for quantum signal transmission, using the collective-rotation noise model.

        Args:
            length: Length of the quantum channel in meters.
            decoherence_rate: Decoherence rate.
        """
        lkm = length / 1000
        standand_lkm = 50.0
        theta = get_rand() * lkm / standand_lkm * np.pi / 4
        operation = np.array([[np.cos(theta), np.sin(theta)], [- np.sin(theta), np.cos(theta)]], dtype=np.complex128)
        self.state.operate(operator=operation)


class BB84SendApp(Application):
    def __init__(self, dest: QNode, qchannel: QuantumChannel,
                 cchannel: ClassicChannel, send_rate=1000,
                 length_for_post_processing=512,
                 ratio_for_estimating_error=0.2,
                 max_cascade_round=5,
                 cascade_alpha=0.73, cascade_beita=2,
                 init_lower_cascade_key_block_size=5,
                 init_upper_cascade_key_block_size=50,
                 security=0.05):
        """
        Initialize BB84SendApp.

        Args:
            dest: Qubit receiver.
            qchannel: Quantum channel.
            cchannel: Classical channel.
            send_rate: Sending rate in bps.
            length_for_post_processing: Length of the key for post-processing.
            ratio_for_estimating_error: Ratio of raw_key used for error rate estimation.
            max_cascade_round: Maximum number of cascade rounds.
            cascade_alpha: Used to calculate the initial block size for cascade, init_size = cascade_alpha / error_rate.
            cascade_beita: Used to update cascade block size, next_size = last_size * 2.
            init_lower_cascade_key_block_size: Lower bound of the initial block size for cascade.
            init_upper_cascade_key_block_size: Upper bound of the initial block size for cascade.
            security: Security parameter for privacy amplification.
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

        self.raw_key_pool = {}  # Raw key pool after basis comparison
        self.fail_number = 0  # Number of failed Qubits during basis comparison

        # Parameters for error correction and privacy amplification
        self.length_for_post_processing = length_for_post_processing
        self.ratio_for_estimating_error = ratio_for_estimating_error
        self.max_cascade_round = max_cascade_round
        self.cascade_alpha = cascade_alpha
        self.cascade_beita = cascade_beita
        self.init_lower_cascade_key_block_size = init_lower_cascade_key_block_size
        self.init_upper_cascade_key_block_size = init_upper_cascade_key_block_size
        self.security = security

        # Parameters for the ongoing post-processing
        self.using_post_processing = False  # Whether post-processing is ongoing
        self.cur_error_rate = 1e-6  # Current error rate during post-processing
        self.cur_cascade_round = 0  # Current cascade round during post-processing
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size  # Current cascade block size
        self.correcting_key = []  # Key being processed
        self.bit_leak = 0  # Number of leaked key bits
        self.shifted_key = []  # Key after post-processing

        self.key_pool = {}  # Key pool

        self.add_handler(self.handleClassicPacket, [RecvClassicPacket], [self.cchannel])  # Handle classical packets

    def install(self, node: QNode, simulator: Simulator):
        """
        Deploy BB84SendApp on a node.

        Args:
            node: Node.
            simulator: Simulation scheduler.
        """
        super().install(node, simulator)
        # Add the first Qubit sending event to the simulator
        t = simulator.ts
        event = func_to_event(t, self.send_qubit, by=self)
        self._simulator.add_event(event)

    def handleClassicPacket(self, node: QNode, event: Event) -> bool:
        """
        Handle classical packets in BB84SendApp.

        Args:
            node: Node.
            event: Simulation event of type RecvClassicPacket.
        Returns:
            bool: Whether the simulation event was handled.
        """
        return self.check_basis(event) or \
            self.recv_error_estimate_packet(event) or \
            self.recv_cascade_ask_packet(event) or \
            self.recv_check_error_ask_packet(event) or \
            self.recv_privacy_amplification_ask_packet(event)

    def check_basis(self, event: RecvClassicPacket) -> bool:
        """
        Compare measurement bases in BB84SendApp based on classical information.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Extract basis comparison packet information
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_CHECK_BASIS:
            return False
        id = msg.get("id")
        basis_dest = msg.get("basis")
        # Compare measurement bases and retain raw_key
        basis_src = "Z" if (self.basis_list[id] == BASIS_Z).all() else "X"
        if basis_dest == basis_src:
            self.raw_key_pool[id] = self.measure_list[id]
        else:
            self.fail_number += 1
        # Clear used Qubits
        self.basis_list.pop(id)
        self.qubit_list.pop(id)
        self.measure_list.pop(id)
        # Send basis comparison packet
        check_packet = ClassicPacket(msg={"packet_class": PACKET_CHECK_BASIS,
                                          "id": id,
                                          "basis": basis_src},
                                     src=self._node,
                                     dest=self.dest)
        self.cchannel.send(packet=check_packet, next_hop=self.dest)

        return True

    def send_qubit(self):
        """
        Randomly prepare and send Qubits in BB84SendApp.
        """
        # Randomly prepare Qubit
        state = get_choice([QUBIT_STATE_0, QUBIT_STATE_1,
                            QUBIT_STATE_P, QUBIT_STATE_N])
        qubit = QubitWithError(state=state)
        # Record measurement basis and measurement result
        basis = BASIS_Z if (state == QUBIT_STATE_0).all() or (
            state == QUBIT_STATE_1).all() else BASIS_X
        ret = 0 if (state == QUBIT_STATE_0).all() or (
            state == QUBIT_STATE_P).all() else 1
        qubit.id = self.count
        self.count += 1
        self.qubit_list[qubit.id] = qubit
        self.basis_list[qubit.id] = basis
        self.measure_list[qubit.id] = ret
        # Send Qubit
        self.qchannel.send(qubit=qubit, next_hop=self.dest)
        # Add the next Qubit sending event
        t = self._simulator.current_time + \
            self._simulator.time(sec=1 / self.send_rate)
        event = func_to_event(t, self.send_qubit, by=self)
        self._simulator.add_event(event)

    def recv_error_estimate_packet(self, event: RecvClassicPacket) -> bool:
        """
        Handle error rate estimation packets in BB84SendApp.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Extract packet information and determine packet type
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_ERROR_ESTIMATE:
            return False

        # Initialize key post-processing information for this round
        self.using_post_processing = True
        self.cur_error_rate = 1e-6
        self.cur_cascade_round = 0
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        self.correcting_key = []
        self.bit_leak = 0

        # Get key information for error rate estimation
        recv_app_bit_for_estimate = msg.get("bit_for_estimate")
        recv_app_bit_index_for_estimate = msg.get("bit_index_for_estimate")
        recv_app_bit_index_for_cascade = msg.get("bit_index_for_cascade")
        keys = list(self.raw_key_pool.keys())[0:self.length_for_post_processing]
        error_in_estimate = 0  # Number of errors in this round
        real_bit_length_for_estimate = 0  # Actual number of keys used for error estimation
        # Extract keys used in this round
        for i in keys:
            item_temp = self.raw_key_pool.pop(i)
            if i in recv_app_bit_index_for_estimate:
                # This bit is used for error estimation
                bit_index = recv_app_bit_index_for_estimate.index(i)
                if item_temp == recv_app_bit_for_estimate[bit_index]:
                    real_bit_length_for_estimate += 1
                else:
                    real_bit_length_for_estimate += 1
                    error_in_estimate += 1
            elif i in recv_app_bit_index_for_cascade:
                # This bit is used for cascade
                self.correcting_key.append(item_temp)

        # Error rate estimation
        self.cur_error_rate = error_in_estimate/real_bit_length_for_estimate
        # Set the initial key block size for error correction based on the error rate
        if self.cur_error_rate <= (self.cascade_alpha/self.init_upper_cascade_key_block_size):
            self.cur_cascade_key_block_size = self.init_upper_cascade_key_block_size
        elif self.cur_error_rate >= (self.cascade_alpha/self.init_lower_cascade_key_block_size):
            self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        else:
            self.cur_cascade_key_block_size = int(self.cascade_alpha/self.cur_error_rate)

        self.cur_cascade_round = 1

        # Send error rate estimation response packet
        packet = ClassicPacket(msg={"packet_class": PACKET_ERROR_ESTIMATE,
                                    "error_rate": self.cur_error_rate},
                               src=self._node,
                               dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

    def recv_cascade_ask_packet(self, event: RecvClassicPacket) -> bool:
        """
        Handle cascade error correction packets in BB84SendApp.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Extract packet information and determine packet type
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_CASCADE:
            return False

        # Get cascade information
        parity_request = msg.get("parity_request")
        round_change_flag = msg.get("round_change_flag")
        shuffle_index = msg.get("shuffle_index")

        # Determine whether to trigger the next cascade round and perform shuffle
        if round_change_flag is True and shuffle_index != []:
            self.cur_cascade_key_block_size = int(self.cur_cascade_key_block_size * self.cascade_beita)
            self.cur_cascade_round += 1
            self.correcting_key = [self.correcting_key[i] for i in shuffle_index]

        # Calculate the parity of all blocks
        parity_answer = []
        for key_interval in parity_request:
            temp_parity = cascade_parity(self.correcting_key[key_interval[0]:key_interval[1]+1])
            parity_answer.append(temp_parity)

        # Send cascade response packet
        packet = ClassicPacket(msg={"packet_class": PACKET_CASCADE,
                                    "parity_answer": parity_answer},
                               src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

    def recv_check_error_ask_packet(self, event: RecvClassicPacket) -> bool:
        """
        Handle error verification packets in BB84SendApp.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Extract packet information and determine packet type
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_CHECK_ERROR:
            return False

        # Extract key block hash value and compare to determine whether error correction was successful
        recv_hash_key = msg.get("hash_key")
        binary_key = int(''.join(str(bit) for bit in self.correcting_key), 2).to_bytes(64, 'big')
        hash_key = hashlib.md5(binary_key).hexdigest()
        if hash_key != recv_hash_key:
            pa_flag = False
            packet = ClassicPacket(msg={"packet_class": PACKET_CHECK_ERROR,
                                        "pa_flag": pa_flag},
                                   src=self._node, dest=self.dest)
        else:
            pa_flag = True
            packet = ClassicPacket(msg={"packet_class": PACKET_CHECK_ERROR,
                                        "pa_flag": pa_flag},
                                   src=self._node, dest=self.dest)
        self.cchannel.send(packet, next_hop=self.dest)
        return True

    def recv_privacy_amplification_ask_packet(self, event: RecvClassicPacket) -> bool:
        """
        Handle privacy amplification packets in BB84SendApp.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Extract packet information and determine packet type
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_PRIVACY_AMPLIFICATION:
            return False
        # Perform privacy amplification
        pa_flag = msg.get("pa_flag")
        if pa_flag is True:
            first_row = msg.get("first_row")
            first_col = msg.get("first_col")
            matrix_row = len(first_row)
            matrix_col = len(first_col)+1
            toeplitz_matrix = pa_generate_toeplitz_matrix(matrix_row, matrix_col, first_row, first_col)
            self.shifted_key += list(pa_randomize_key(self.correcting_key, toeplitz_matrix))
            self.using_post_processing = False
        # Fill the key pool
        if len(self.shifted_key) >= KEY_BLOCK_SIZE:
            new_key_block = self.shifted_key[:KEY_BLOCK_SIZE]
            self.shifted_key = self.shifted_key[KEY_BLOCK_SIZE:]
            binary_key = int(''.join(str(bit) for bit in new_key_block), 2).to_bytes(64, 'big')
            new_key_id = hashlib.md5(binary_key).hexdigest()
            self.key_pool[new_key_id] = new_key_block

        return True


class BB84RecvApp(Application):
    def __init__(self, src: QNode, qchannel: QuantumChannel, cchannel: ClassicChannel,
                 length_for_post_processing=512,
                 ratio_for_estimating_error=0.2, max_cascade_round=5,
                 cascade_alpha=0.73, cascade_beita=2,
                 init_lower_cascade_key_block_size=5,
                 init_upper_cascade_key_block_size=50,
                 security=0.05):
        """
        Initialize BB84RecvApp.

        Args:
            src: Qubit sending node.
            qchannel: Quantum channel.
            cchannel: Classical channel.
            length_for_post_processing: Length of the key for post-processing.
            ratio_for_estimating_error: Ratio of raw_key used for error rate estimation.
            max_cascade_round: Maximum number of cascade rounds.
            cascade_alpha: Used to calculate the initial block size for cascade, init_size = cascade_alpha / error_rate.
            cascade_beita: Used to update cascade block size, next_size = last_size * 2.
            init_lower_cascade_key_block_size: Lower bound of the initial block size for cascade.
            init_upper_cascade_key_block_size: Upper bound of the initial block size for cascade.
            security: Security parameter for privacy amplification.
        """
        super().__init__()
        self.src = src
        self.qchannel = qchannel
        self.cchannel = cchannel

        self.qubit_list = {}
        self.basis_list = {}
        self.measure_list = {}

        self.raw_key_pool = {}  # Raw key pool after basis comparison
        self.fail_number = 0  # Number of failed Qubits during basis comparison

        # Parameters for error correction and privacy amplification
        self.length_for_post_processing = length_for_post_processing
        self.ratio_for_estimating_error = ratio_for_estimating_error
        self.max_cascade_round = max_cascade_round
        self.cascade_alpha = cascade_alpha
        self.cascade_beita = cascade_beita
        self.init_lower_cascade_key_block_size = init_lower_cascade_key_block_size
        self.init_upper_cascade_key_block_size = init_upper_cascade_key_block_size
        self.security = security

        # Parameters for the ongoing post-processing
        self.using_post_processing = False  # Whether post-processing is ongoing
        self.cascade_round_atbegin = False  # Whether at the beginning of a cascade round
        self.cur_error_rate = 1e-6  # Current error rate during post-processing
        self.cur_cascade_round = 0  # Current cascade round during post-processing
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size  # Current cascade block size
        self.correcting_key = []  # Key being corrected
        self.cascade_binary_set = []  # Cascade block information
        self.bit_leak = 0  # Number of leaked key bits
        self.shifted_key = []  # Key after post-processing

        self.key_pool = {}  # Key pool

        self.add_handler(self.handleQuantumPacket, [RecvQubitPacket], [self.qchannel])  # Handle Qubits
        self.add_handler(self.handleClassicPacket, [RecvClassicPacket], [self.cchannel])  # Handle classical packets

    def handleQuantumPacket(self, node: QNode, event: Event) -> bool:
        """
        Handle received Qubits in BB84RecvApp.

        Args:
            node: Node.
            event: Simulation event of type RecvQubitPacket.
        Returns:
            bool: Whether the simulation event was handled.
        """
        return self.recv(event)

    def handleClassicPacket(self, node: QNode, event: Event) -> bool:
        """
        Handle classical packets in BB84RecvApp.

        Args:
            node: Node.
            event: Simulation event of type RecvClassicPacket.
        Returns:
            bool: Whether the simulation event was handled.
        """
        return self.check_basis(event) or \
            self.recv_error_estimate_reply_packet(event) or \
            self.recv_cascade_reply_packet(event) or \
            self.recv_check_error_reply_packet(event)

    def check_basis(self, event: RecvClassicPacket):
        """
        Compare measurement bases in BB84RecvApp based on classical information.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Extract basis comparison packet information
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_CHECK_BASIS:
            return False
        id = msg.get("id")
        basis_src = msg.get("basis")
        # Compare measurement bases and retain raw_key
        basis_dest = "Z" if (self.basis_list[id] == BASIS_Z).all() else "X"
        if basis_dest == basis_src:
            self.raw_key_pool[id] = self.measure_list[id]
        else:
            self.fail_number += 1
        # Clear used Qubits
        self.basis_list.pop(id)
        self.qubit_list.pop(id)
        self.measure_list.pop(id)
        # Sufficient keys for post-processing
        if self.using_post_processing is False and len(self.raw_key_pool) >= self.length_for_post_processing:
            self.send_error_estimate_packet()

        return True

    def recv(self, event: RecvQubitPacket) -> bool:
        """
        Receive Qubits in BB84RecvApp, randomly select measurement bases, and measure Qubits.

        Args:
            event: Simulation event for receiving Qubits.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Random measurement
        qubit: Qubit = event.qubit
        basis = get_choice([BASIS_Z, BASIS_X])
        basis_msg = "Z" if (basis == BASIS_Z).all() else "X"
        ret = qubit.measureZ() if (basis == BASIS_Z).all() else qubit.measureX()
        # Record measurement result
        self.qubit_list[qubit.id] = qubit
        self.basis_list[qubit.id] = basis
        self.measure_list[qubit.id] = ret
        # Send basis comparison packet
        check_packet = ClassicPacket(msg={"packet_class": PACKET_CHECK_BASIS,
                                          "id": qubit.id,
                                          "basis": basis_msg},
                                     src=self._node,
                                     dest=self.src)
        self.cchannel.send(check_packet, next_hop=self.src)

        return True

    def send_error_estimate_packet(self):
        """
        Send error rate estimation packets in BB84RecvApp.
        """
        # Initialize post-processing information
        self.using_post_processing = True
        self.cascade_round_atbegin = True
        self.cur_cascade_round = 0
        self.cur_error_rate = 1e-6
        self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        self.correcting_key = []
        self.cascade_binary_set = []
        self.bit_leak = 0

        # Get key index information
        bit_for_estimate = {}
        bit_for_postporcessing = {}
        keys = list(self.raw_key_pool.keys())[0:self.length_for_post_processing]

        # Randomly select keys for error rate estimation
        for i in keys:
            item_temp = self.raw_key_pool.pop(i)
            if get_rand(0, 1) < self.ratio_for_estimating_error:
                bit_for_estimate[i] = item_temp
            else:
                self.correcting_key.append(item_temp)
                bit_for_postporcessing[i] = item_temp

        # Send error rate estimation packet
        packet = ClassicPacket(msg={"packet_class": PACKET_ERROR_ESTIMATE,
                                    "bit_index_for_estimate": list(bit_for_estimate.keys()),
                                    "bit_for_estimate": list(bit_for_estimate.values()),
                                    "bit_index_for_cascade": list(bit_for_postporcessing.keys())},
                               src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

    def recv_error_estimate_reply_packet(self, event: RecvClassicPacket) -> bool:
        """
        Handle error rate estimation reply packets in BB84RecvApp and start the first cascade round.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Determine packet type
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_ERROR_ESTIMATE:
            return False

        # Extract error rate information and set initial block size
        self.cur_error_rate = msg.get("error_rate")
        if self.cur_error_rate <= (self.cascade_alpha/self.init_upper_cascade_key_block_size):
            self.cur_cascade_key_block_size = self.init_upper_cascade_key_block_size
        elif self.cur_error_rate >= (self.cascade_alpha/self.init_lower_cascade_key_block_size):
            self.cur_cascade_key_block_size = self.init_lower_cascade_key_block_size
        else:
            self.cur_cascade_key_block_size = int(self.cascade_alpha/self.cur_error_rate)

        self.cur_cascade_round = 1

        # Divide cascade into blocks
        count_temp = 0
        last_index = len(self.correcting_key) - 1
        while count_temp <= last_index:
            end = count_temp + self.cur_cascade_key_block_size - 1
            if end <= last_index:
                self.cascade_binary_set.append((count_temp, end))
                count_temp = end + 1
            else:
                end = last_index
                self.cascade_binary_set.append((count_temp, end))
                break

        # Send cascade packet
        packet = ClassicPacket(msg={"packet_class": PACKET_CASCADE,
                                    "parity_request": self.cascade_binary_set,
                                    "round_change_flag": False,
                                    "shuffle_index": []},
                               src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)

        return True

    def recv_cascade_reply_packet(self, event: RecvClassicPacket):
        """
        Handle cascade reply packets in BB84RecvApp and execute subsequent cascade rounds.

        Args:
            event: Simulation event for receiving classical packets.
        Returns:
            bool: Whether the simulation event was handled.
        """
        # Determine packet type
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_CASCADE:
            return False

        # Get cascade response data
        parity_answer = msg.get("parity_answer")
        # Estimate leaked information
        if self.cascade_round_atbegin is True:
            self.bit_leak += len(parity_answer)
            self.cascade_round_atbegin = False
        else:
            self.bit_leak += int(len(parity_answer)/2)

        # Compare parity values and perform binary division for blocks with odd errors
        count_temp = 0  # Key block index
        copy_cascade_binary_set = self.cascade_binary_set.copy()
        for key_interval in copy_cascade_binary_set:
            temp_parity = cascade_parity(self.correcting_key[key_interval[0]:key_interval[1]+1])
            if temp_parity == parity_answer[count_temp]:
                # Key block has even errors (including 0), cannot be corrected
                self.cascade_binary_set.remove(key_interval)
            elif key_interval[0] != key_interval[1]:
                # Key block has odd errors, perform binary division
                self.cascade_binary_set.remove(key_interval)
                left_temp, right_temp = cascade_binary_divide(key_interval[0], key_interval[1])
                self.cascade_binary_set.append(left_temp)
                self.cascade_binary_set.append(right_temp)
            else:
                # Locate the position of odd errors
                self.cascade_binary_set.remove(key_interval)
                self.correcting_key[key_interval[0]] = parity_answer[count_temp]

            count_temp += 1

        # Determine whether to change cascade round
        round_change_flag = False
        check_error_flag = False
        shuffle_index = []
        if len(self.cascade_binary_set) == 0:
            if self.cur_cascade_round == self.max_cascade_round:  # Reached maximum cascade rounds
                check_error_flag = True
                binary_key = int(''.join(str(bit) for bit in self.correcting_key), 2).to_bytes(64, 'big')
                hash_key = hashlib.md5(binary_key).hexdigest()
            else:  # Not reached maximum cascade rounds
                # Update initial information for the next cascade round
                round_change_flag = True
                self.cascade_round_atbegin = True
                self.cur_cascade_round += 1
                self.cur_cascade_key_block_size = int(self.cur_cascade_key_block_size * self.cascade_beita)
                # Perform shuffle
                shuffle_index = [i for i in range(len(self.correcting_key))]
                shuffle_index = cascade_key_shuffle(shuffle_index)
                self.correcting_key = [self.correcting_key[i] for i in shuffle_index]
                # Initial block division
                count_temp = 0
                last_index = len(self.correcting_key) - 1
                while count_temp <= last_index:
                    end = count_temp + self.cur_cascade_key_block_size - 1
                    if end <= last_index:
                        self.cascade_binary_set.append((count_temp, end))
                        count_temp = end + 1
                    else:
                        end = last_index
                        self.cascade_binary_set.append((count_temp, end))
                        break

        # Send cascade error correction request packet
        if check_error_flag is False:
            packet = ClassicPacket(msg={"packet_class": PACKET_CASCADE,
                                        "parity_request": self.cascade_binary_set,
                                        "round_change_flag": round_change_flag,
                                        "shuffle_index": shuffle_index},
                                   src=self._node, dest=self.src)
        else:
            # Send error comparison packet
            packet = ClassicPacket(msg={"packet_class": PACKET_CHECK_ERROR,
                                        "hash_key": hash_key},
                                   src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)
        return True

    def recv_check_error_reply_packet(self, event: RecvClassicPacket):
        """
        Handle error verification reply packets in BB84RecvApp.

        Args:
            event: The check_error_reply packet.
        """
        packet = event.packet
        msg: dict = packet.get()
        packet_class = msg.get("packet_class")
        if packet_class != PACKET_CHECK_ERROR:
            return False
        pa_flag = msg.get("pa_flag")
        if pa_flag is True:
            # Error verification successful, perform privacy amplification
            matrix_row = len(self.correcting_key)
            matrix_col = (1-self.security)*len(self.correcting_key)-self.bit_leak
            first_row = [get_choice([0, 1]) for _ in range(matrix_row)]
            first_col = [get_choice([0, 1]) for _ in range(int(matrix_col)-1)]
            toeplitz_matrix = pa_generate_toeplitz_matrix(matrix_row, matrix_col, first_row, first_col)
            self.shifted_key += list(pa_randomize_key(self.correcting_key, toeplitz_matrix))
            packet = ClassicPacket(msg={"packet_class": PACKET_PRIVACY_AMPLIFICATION,
                                        "pa_flag": True,
                                        "first_row": first_row,
                                        "first_col": first_col},
                                   src=self._node, dest=self.src)
            self.using_post_processing = False
        else:
            # Error verification failed, discard
            first_row = []
            first_col = []
            packet = ClassicPacket(msg={"packet_class": PACKET_PRIVACY_AMPLIFICATION,
                                        "pa_flag": False,
                                        "first_row": first_row,
                                        "first_col": first_col},
                                   src=self._node, dest=self.src)
            self.using_post_processing = False
        self.cchannel.send(packet, next_hop=self.src)
        # Fill the key pool
        if len(self.shifted_key) >= KEY_BLOCK_SIZE:
            new_key_block = self.shifted_key[:KEY_BLOCK_SIZE]
            self.shifted_key = self.shifted_key[KEY_BLOCK_SIZE:]
            binary_key = int(''.join(str(bit) for bit in new_key_block), 2).to_bytes(64, 'big')
            new_key_id = hashlib.md5(binary_key).hexdigest()
            self.key_pool[new_key_id] = new_key_block
        return True