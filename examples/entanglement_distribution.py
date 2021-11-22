from typing import ChainMap, Dict, List, Optional, Tuple
import uuid
import logging

from qns.entity.cchannel.cchannel import ClassicChannel, ClassicPacket, RecvClassicPacket
from qns.entity.memory.memory import OutOfMemoryException, QuantumMemory
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.entity.qchannel.qchannel import QuantumChannel, RecvQubitPacket
from qns.models.core.backend import QuantumModel
from qns.network.requests import Request
from qns.network.route.dijkstra import DijkstraRouteAlgorithm
from qns.network.topology.topo import ClassicTopology
from qns.simulator.event import Event, func_to_event
from qns.simulator.simulator import Simulator
from qns.network import QuantumNetwork
from qns.models.epr import WernerStateEntanglement
from qns.simulator.ts import Time
from qns.network.topology import RandomTopology, LineTopology
import qns.utils.log as log

log.logger.setLevel(logging.DEBUG)

# constrains
init_fidelity = 0.99
nodes_number = 5
lines_number = 4
qchannel_delay = 0.01
cchannel_delay = 0.01
memory_capacity = 3
send_rate = 1

class Transmit():
    def __init__(self, id: str, src: QNode, dst: QNode, first_epr_name: Optional[str] = None, second_epr_name: Optional[str] = None):
        self.id = id
        self.src = src
        self.dst = dst
        self.first_epr_name = first_epr_name
        self.second_epr_name = second_epr_name
    
    def __repr__(self) -> str:
        return f"<transmit {self.id}: {self.src} -> {self.dst}, epr: {self.first_epr_name}, {self.second_epr_name}>"

class EntanglementDistributionApp(Application):
    def __init__(self, net: QuantumNetwork ,send_rate: Optional[int] = None):
        super().__init__()
        self.net = net

        self.own: QNode = None
        self.memory: QuantumMemory = None
        self.src: Optional[QNode] = None
        self.dst: Optional[QNode] = None
        self.send_rate: int = send_rate

        self.send_idx = 0

        self.state: Dict[str, Transmit] = {}

        self.success = []

    def install(self, node: QNode, simulator: Simulator):
        super().install(node, simulator)
        self.own: QNode = self._node
        self.memory: QuantumMemory = self.own.memories[0]
        try:
            request: Request = self.own.requests[0]
            if self.own == request.src:
                self.dst = request.dest
            elif self.own == request.dest:
                self.src = request.src
            self.send_rate = request.attr.get("send_rate")
        except IndexError:
            pass
        
        if self.dst is not None:
            # I am a sender
            t = simulator.ts
            event = func_to_event(t, self.new_distribution)
            self._simulator.add_event(event)

    def handle(self, node: QNode, event: Event):
        if isinstance(event, RecvQubitPacket):
            self.response_distribution(event)
        elif isinstance(event, RecvClassicPacket):
            self.handle_response(event)

    def new_distribution(self):

        # insert the next send event
        t = self._simulator.tc+ Time(sec=1/self.send_rate)
        event = func_to_event(t, self.new_distribution)
        self._simulator.add_event(event)
        log.debug(f"{self.own}: start new request")

        # generate new entanglement
        try:
            epr = self.generate_qubit(self.own, self.dst, None)
            log.debug(f"{self.own}: generate epr {epr.name}")

            self.state[epr.transmit_id] = Transmit(
                id = epr.transmit_id, 
                src = self.own, 
                dst = self.dst, 
                second_epr_name= epr.name)
    
            log.debug(f"{self.own}: generate transmit {self.state[epr.transmit_id]}")
            self.memory.write(epr)
        except OutOfMemoryException:
            self.memory.read(epr)
            self.state[epr.transmit_id] = None
        self.request_distrbution(epr.transmit_id)
    
    def request_distrbution(self, transmit_id: str):
        transmit = self.state.get(transmit_id)
        if transmit is None:
            return
        epr_name = transmit.second_epr_name
        epr = self.memory.get(epr_name)
        if epr is None:
            return
        
        dst = transmit.dst
        # get next hop
        route_result = self.net.query_route(self.own, dst)
        try:
            next_hop:QNode = route_result[0][1]
        except IndexError:
            raise Exception("Route error")
        
        qchannel: QuantumChannel = self.own.get_qchannel(next_hop)
        if qchannel is None:
            raise Exception("No such quantum channel")

        # send the entanglement
        log.debug(f"{self.own}: send epr {epr.name} to {next_hop}")
        qchannel.send(epr, next_hop)

    def response_distribution(self, packet: RecvQubitPacket):
        qchannel: QuantumChannel = packet.qchannel
        from_node: QNode = qchannel.node_list[0] if qchannel.node_list[1] == self.own else qchannel.node_list[1]

        cchannel: ClassicChannel = self.own.get_cchannel(from_node)
        if cchannel is None:
            raise Exception("No such classic channel")

        # receive the first epr
        epr: WernerStateEntanglement = packet.qubit
        log.debug(f"{self.own}: recv epr {epr.name} from {from_node}")

        # generate the second epr
        next_epr = self.generate_qubit(src = epr.src, dst = epr.dst, transmit_id = epr.transmit_id)
        log.debug(f"{self.own}: generate epr {next_epr.name}")
        self.state[epr.transmit_id] = Transmit(
            id = epr.transmit_id, 
            src = epr.src, 
            dst = epr.dst, 
            first_epr_name= epr.name,
            second_epr_name= next_epr.name)
        log.debug(f"{self.own}: generate transmit {self.state[epr.transmit_id]}")

        try:
            #try to restore those entanglements
            log.debug(f"{self.own}: store {epr.name} and {next_epr.name}")
            self.memory.write(epr)
            self.memory.write(next_epr)
        except:
            log.debug(f"{self.own}: store fail, destory {epr} and {next_epr}")
            # if failed (memory is full), destory all entanglements
            self.memory.read(epr)
            self.memory.read(next_epr)
            classic_packet = ClassicPacket(msg = {"cmd": "revoke", "transmit_id": epr.transmit_id}, src = self.own, dst = from_node)
            cchannel.send(classic_packet, next_hop = from_node)
            log.debug(f"{self.own}: send {classic_packet.msg} to {from_node}")
            return

        classic_packet = ClassicPacket(msg = {"cmd": "swap", "transmit_id": epr.transmit_id}, src = self.own, dest = from_node)
        cchannel.send(classic_packet, next_hop = from_node)
        log.debug(f"{self.own}: send {classic_packet.msg} from {self.own} to {from_node}")

    def handle_response(self, packet: RecvClassicPacket):
        msg = packet.packet.get()
        cchannel = packet.cchannel

        from_node: QNode = cchannel.node_list[0] if cchannel.node_list[1] == self.own else cchannel.node_list[1]

        log.debug(f"{self.own}: recv {msg} from {from_node}")

        cmd = msg["cmd"]
        transmit_id = msg["transmit_id"]
        transmit = self.state.get(transmit_id)

        if cmd == "swap":
            if self.own != transmit.src:
                # perfrom entanglement swapping
                first_epr: WernerStateEntanglement = self.memory.read(transmit.first_epr_name)
                second_epr: WernerStateEntanglement = self.memory.read(transmit.second_epr_name)
                new_epr = first_epr.swapping(second_epr, name = uuid.uuid4().hex)
                log.debug(f"{self.own}:perform swap use {first_epr} and {second_epr}")
                log.debug(f"{self.own}:perform swap generate {new_epr}")
            
                src: QNode = transmit.src
                app:EntanglementDistributionApp = src.get_apps(EntanglementDistributionApp)[0]
                app.set_second_epr(new_epr, transmit_id= transmit_id)
                print(1, src, app.state)

                app:EntanglementDistributionApp = from_node.get_apps(EntanglementDistributionApp)[0]
                app.set_first_epr(new_epr, transmit_id= transmit_id)
                print(2, from_node, app.state)

            classic_packet = ClassicPacket(msg = {"cmd": "next", "transmit_id": transmit_id}, src = self.own, dest = from_node)
            cchannel.send(classic_packet, next_hop = from_node)
            log.debug(f"{self.own}: send {classic_packet.msg} to {from_node}")
        elif cmd == "next":
            # finish or request to the next hop
            if self.own == transmit.dst:
                result_epr = self.memory.read(transmit.first_epr_name)
                self.memory.read(transmit.second_epr_name)
                self.success.append(result_epr)
                self.state[transmit_id] = None
                log.debug(f"{self.own}: successful distribute {result_epr}")
            else:
                log.debug(f"{self.own}: begin new request {transmit_id}")
                self.request_distrbution(transmit_id)
        else:
            # clean memory
            log.debug(f"{self.own}: clean memory {transmit.first_epr_name} and {transmit.second_epr_name}")
            self.memory.read(transmit.first_epr_name)
            self.memory.read(transmit.second_epr_name)
            self.state[transmit_id] = None
            if self.own != transmit.src:
                classic_packet = ClassicPacket(msg = {"cmd": "revoke", "transmit_id": transmit_id}, src = self.own, dest = transmit.src)
                cchannel = self.own.get_cchannel(transmit.src)
                if cchannel is not None:
                    log.debug(f"{self.own}: send {classic_packet} to {from_node}")
                    cchannel.send(classic_packet, next_hop = transmit.src)

    def generate_qubit(self, src: QNode, dst: QNode, transmit_id: Optional[str] = None) -> QuantumModel:
        epr = WernerStateEntanglement(fidelity = init_fidelity, name = uuid.uuid4().hex)
        epr.src = src
        epr.dst = dst
        epr.transmit_id = transmit_id if transmit_id is not None else uuid.uuid4().hex
        return epr

    def set_first_epr(self, epr: QuantumModel, transmit_id: str):
        transmit = self.state.get(transmit_id, None)
        if transmit is None or transmit.first_epr_name is None:
            return
        self.memory.read(transmit.first_epr_name)
        self.memory.write(epr)
        transmit.first_epr_name = epr.name

    def set_second_epr(self, epr: QuantumModel, transmit_id: str):
        transmit = self.state.get(transmit_id, None)
        if transmit is None or transmit.second_epr_name is None:
            return
        self.memory.read(transmit.second_epr_name)
        self.memory.write(epr)
        transmit.second_epr_name = epr.name


s = Simulator(0, 10, accuracy=1000000)
log.install(s)
topo = LineTopology(nodes_number= nodes_number,
    qchannel_args={"delay": qchannel_delay},
    cchannel_args={"delay": cchannel_delay},
    memory_args={"capacity": memory_capacity})
    
net = QuantumNetwork(topo = topo, classic_topo= ClassicTopology.All, route = DijkstraRouteAlgorithm())
net.build_route()

src = net.get_node("n1")
dst = net.get_node(f"n{nodes_number}")
net.add_request(src = src, dest = dst, attr={"send_rate": send_rate})

for n in net.nodes:
    n.add_apps(EntanglementDistributionApp(net))

for n in net.nodes:
    n.install(s)

s.run()