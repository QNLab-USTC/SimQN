from numpy.lib.arraysetops import isin
from qns.entity.cchannel.cchannel import ClassicChannel, RecvClassicPacket
from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel, RecvQubitPacket
from qns.entity import QNode
from qns.entity.timer.timer import Timer
from qns.models.qubit.const import BASIS_X, BASIS_Z
from qns.simulator.event import Event, func_to_event
from qns.simulator.simulator import Simulator
from qns.models.qubit import Qubit, QUBIT_STATE_0, QUBIT_STATE_1, QUBIT_STATE_P, QUBIT_STATE_N
from qns.models.qubit.gate import R
from qns.entity import ClassicPacket
import qns.utils.log as log

from random import choice
import numpy as np


class QubitWithError(Qubit):
    def transfer_error_model(self, length: float, **kwargs):
        # lkm = length / 1000
        # R(self, np.pi /4)
        pass


class BB84SendApp(Application):

    def __init__(self, dest: QNode, qchannel: QuantumChannel, cchannel: ClassicChannel, send_rate=1000):
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

        qubit = self.qubit_list[id]
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
        basis_msg = "Z" if (basis == BASIS_Z).all() else "X"

        ret = 0 if (state == QUBIT_STATE_0).all() or (
            state == QUBIT_STATE_P).all() else 1

        qubit.id = self.count
        self.count += 1
        self.qubit_list[qubit.id] = qubit
        self.basis_list[qubit.id] = basis
        self.measure_list[qubit.id] = ret

        # log.info(f"[{self._simulator.current_time}] send qubit {qubit.id}, basis: {basis_msg} , ret: {ret}")
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

        qubit = self.qubit_list[id]
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
        # randomly choise X,Z basis
        basis = choice([BASIS_Z, BASIS_X])
        basis_msg = "Z" if (basis == BASIS_Z).all() else "X"
        ret = qubit.measureZ() if (basis == BASIS_Z).all() else qubit.measureX()
        self.qubit_list[qubit.id] = qubit
        self.basis_list[qubit.id] = basis
        self.measure_list[qubit.id] = ret

        # log.info(f"[{self._simulator.current_time}] recv qubit {qubit.id},basis: {basis_msg}, ret: {ret}")
        packet = ClassicPacket(
            msg={"id": qubit.id, "basis": basis_msg}, src=self._node, dest=self.src)
        self.cchannel.send(packet, next_hop=self.src)


light_speed = 299791458

def drop_rate(length):
    # drop 0.2 db/KM
    return 1 - np.exp(- length / 50000)


for length in [1000, 5000, 10000, 50000, 100000, 150000]:
    results = []
    for i in range(10):
        s = Simulator(0, 10, accuracy=10000000000)
        n1 = QNode(name="n1")
        n2 = QNode(name="n2")
    
        qlink = QuantumChannel(name="l1", delay=length /
                            light_speed, drop_rate=drop_rate(length))
    
        clink = ClassicChannel(name="c1", delay=length/light_speed)             
    
        n1.add_cchannel(clink)
        n2.add_cchannel(clink)
        n1.add_qchannel(qlink)
        n2.add_qchannel(qlink)
    
        sp = BB84SendApp(n2, qlink, clink, send_rate=1000)
        rp = BB84RecvApp(n1, qlink, clink)
        n1.add_apps(sp)
        n2.add_apps(rp)
    
        n1.install(s)
        n2.install(s)
    
        s.run()
        results.append(len(rp.succ_key_pool) / 10)
    print(length, np.mean(results), np.std(results))
