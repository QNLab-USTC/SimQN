from qns.quantum.protocol.protocol import NodeProtocol
from qns.quantum.qubit import Qubit
from qns.quantum.entity import Node, Memory, MemoryReadEvent, MemoryWriteEvent, MemoryGetEvent, MemoryResultEvent
from qns.schedular import Simulator, Protocol
from qns.log import log

class TestMemoryProtocol(NodeProtocol):
    def __init__(_self, entity, memory: Memory):
        super().__init__(entity)
        _self.memory = memory

    def run(_self, simulator: Simulator):
        q = Qubit(birth_time_slice= simulator.current_time_slice)
        e = MemoryWriteEvent(q)
        _self.memory.call(simulator, msg = "", source= _self.entity, event = e, time_slice= 0)

        while True:
            (msg, source, event) =  yield None

            if not isinstance(event, MemoryResultEvent):
                raise AssertionError("Not MemoryResultEvent")

            if isinstance(event.original_event, MemoryWriteEvent):

                if event.status != MemoryResultEvent.StatusOK:
                    log.info("write result status code error:"+str(event.status))

                idx = event.index
                q = event.qubit
                if idx != None:
                    ge = MemoryGetEvent(by = idx)
                    _self.memory.call(simulator, msg = "", source= _self.entity, event = ge, time_slice= simulator.current_time_slice + simulator.to_time_slice(1))

                re = MemoryReadEvent(by = q)
                _self.memory.call(simulator, msg = "", source= _self.entity, event = re, time_slice= simulator.current_time_slice + simulator.to_time_slice(2))

                q = Qubit(birth_time_slice= simulator.current_time_slice + simulator.to_time_slice(1))
                we = MemoryWriteEvent(q)
                _self.memory.call(simulator, msg = "", source= _self.entity, event = we, time_slice= simulator.current_time_slice + simulator.to_time_slice(1))

            elif isinstance(event.original_event, MemoryReadEvent):
                if event.status != MemoryResultEvent.StatusOK:
                    log.info("write result status code error:"+str(event.status))
                else:
                    q = event.qubit
                    log.info(f"{_self.entity} read {q} at {simulator.current_time}")
            
            elif isinstance(event.original_event, MemoryGetEvent):
                if event.status != MemoryResultEvent.StatusOK:
                    log.info("write result status code error:"+str(event.status))
                else:
                    q = event.qubit
                    log.info(f"{_self.entity} get {q} at {simulator.current_time}")
            else:
                raise AssertionError("error")

s = Simulator(0, 10, 1000)
log.install(s)
log.set_debug(True)


n1 = Node("n1")
m1 = Memory(size = 3, delay= 0.033)
n1.add_subentity(m1)

mp = TestMemoryProtocol(n1, m1)
n1.inject_protocol(mp)

n1.install(s)
s.run()



