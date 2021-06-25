from os import stat
from typing import Any, List, Optional, Union
from qns.schedular import Entity, Event, Simulator
from qns.schedular.entity import RecieveEvent
from qns.quantum.qubit import *


class MemoryWriteEvent(Event):
    '''
    This event is the API to notify memory to write a qubit

    :param qubit: the qubit
    :param index: (optional) to store the qubit in a certain index
    '''

    def __init__(self, qubit: Qubit, index: Optional[int] = None, init_time=None):
        super().__init__(init_time)
        self.qubit = qubit
        self.index = index


class MemoryReadEvent(Event):
    '''
    This event is the API to notify memory to read a qubit

    :param by: a qubit or its name or its index in this memory
    '''

    def __init__(self, by: Union[Qubit, str, int], init_time=None):
        super().__init__(init_time)
        self.by = by


class MemoryGetEvent(Event):
    '''
    This event is the API to get a qubit's information from memory without read it

    :param by: a qubit or its name or its index in this memory
    '''

    def __init__(self, by: Union[Qubit, str, int], init_time=None):
        super().__init__(init_time)
        self.by = by


class MemoryResultEvent(Event):
    '''
    This event returns the result of write or read of quantum memory.

    :param status: a status code below
    :param qubit: the readed qubit
    :param index: the index of that qubit in memory
    :param original_event: the original event that causes this MemoryResultEvent 
    '''

    StatusOK = 0
    StatusCommonError = 1
    StatusIndexError = 2
    StatusFullError = 3
    StatusNotFoundError = 4

    def __init__(self, status: int, qubit: Optional[Qubit] = None, index: Optional[int] = None, original_event: Optional[Union[MemoryGetEvent, MemoryReadEvent, MemoryWriteEvent]] = None, init_time: int = None):
        super().__init__(init_time)
        self.status = status
        self.index = index
        self.qubit = qubit
        self.original_event = original_event


class Memory(Entity):
    '''
        Memory is a sub-entity in node. It can store and access qubit.

        :param name: its name.
        :param size: its size.
        :param delay: the read or write operation time in second.
        :param fidelity_model: its fidelity_model which will decide the status of qubit when the qubit is readed.
        '''

    def __init__(self, size: int = None, delay: int = 0 ,fidelity_model=None,  name: Optional[str] = None):
        super().__init__(name)
        self.size = size
        self.delay = delay
        self.fidelity_model = fidelity_model
        self.registers: List[Optional[Qubit]] = [None] * self.size

    def handle(self, simulator: Simulator, msg: object, source =None, event: Event = None):

        if isinstance(event, MemoryWriteEvent):
            e = self.Write(event.qubit, event.index)
        elif isinstance(event, MemoryReadEvent):
            e = self.Read(event.by)
        elif isinstance(event, MemoryGetEvent):
            e = self.Get(event.by)
        
        # change the fidelity of the reading qubit.
        if isinstance(e, MemoryResultEvent) and e.qubit is not None:
            if self.fidelity_model is not None:
                self.fidelity_model(e.qubit)
            else:
                self.default_fidelity_model(e.qubit)
        
        e.original_event = event
        source.call(simulator, msg = None, source = self, event = e, time_slice = simulator.current_time_slice + simulator.to_time_slice(self.delay))
        # self.simulator.add_event(self.simulator.current_time_slice + self.simulator.to_time_slice(self.delay), e)

    @property
    def full(self) -> bool:
        '''
        Get whether this quantum registers is full

        :return bool: whether it is full or not
        '''
        for _, v in enumerate(self.registers):
            if v is not None:
                return False
        return True

    def default_fidelity_model(self, qubit: Qubit) -> None:
        pass

    def Write(self, qubit, index=None) -> MemoryResultEvent:
        '''
        ''Write''function can store qubit in the specified location.

        :param qubit:the qubit to be stored.
        :param index:the address.
        '''

        if index is None:
            for i, q in enumerate(self.registers):
                if q is None:
                    self.registers[i] = qubit
                    return MemoryResultEvent(MemoryResultEvent.StatusOK, qubit = qubit, index=i)
            return MemoryResultEvent(MemoryResultEvent.StatusFullError)

        if index < 0 or index >= self.size:
            return MemoryResultEvent(MemoryResultEvent.StatusIndexError)

        if self.registers[index] is not None:
            return MemoryResultEvent(MemoryResultEvent.StatusFullError)

        self.registers[index] = qubit
        return MemoryResultEvent(MemoryResultEvent.StatusOK, qubit = qubit, index=index)

    def Read(self, by: Union[Qubit, str, int]) -> MemoryResultEvent:
        '''
        ''Read''function can read qubit in the specified location.

        :param by: a qubit or its name or its index in this memory
        '''

        if isinstance(by, Qubit):
            #  by is a qubit
            for i, v in enumerate(self.registers):
                if isinstance(v, Qubit) and v == by:
                    self.registers[i] = None
                    return MemoryResultEvent(MemoryResultEvent.StatusOK, by)
            return MemoryResultEvent(MemoryResultEvent.StatusNotFoundError)
        elif isinstance(by, str):
            # by is a name
            for i, v in enumerate(self.registers):
                if isinstance(v, Qubit) and v.name == by:
                    self.registers[i] = None
                    return MemoryResultEvent(MemoryResultEvent.StatusOK, v)
            return MemoryResultEvent(MemoryResultEvent.StatusNotFoundError)
        elif isinstance(by, int):
            if by < 0 or by >= self.size:
                return MemoryResultEvent(MemoryResultEvent.StatusIndexError)

            if self.registers[by] is None:
                return MemoryResultEvent(MemoryResultEvent.StatusNotFoundError)

            qubit = self.registers[by]
            self.registers[by] = None
            return MemoryResultEvent(MemoryResultEvent.StatusOK, qubit)

        return MemoryResultEvent(MemoryResultEvent.StatusCommonError)

    def Get(self, by: Union[Qubit, str, int]) -> MemoryResultEvent:
        '''
        ''Get'' function can get the information of a qubit without read it.

        :param by: a qubit or its name or its index in this memory
        '''

        if isinstance(by, Qubit):
            #  by is a qubit
            if by in self.registers:
                return MemoryResultEvent(MemoryResultEvent.StatusOK, by)
            return MemoryResultEvent(MemoryResultEvent.StatusNotFoundError)
        elif isinstance(by, str):
            # by is a name
            for i, v in enumerate(self.registers):
                if isinstance(v, Qubit) and v.name == by:
                    return MemoryResultEvent(MemoryResultEvent.StatusOK, v)
            return MemoryResultEvent(MemoryResultEvent.StatusNotFoundError)
        elif isinstance(by, int):
            if by < 0 or by >= self.size:
                return MemoryResultEvent(MemoryResultEvent.StatusIndexError)

            if self.registers[by] is None:
                return MemoryResultEvent(MemoryResultEvent.StatusNotFoundError)

            qubit = self.registers[by]
            return MemoryResultEvent(MemoryResultEvent.StatusOK, qubit)

        return MemoryResultEvent(MemoryResultEvent.StatusCommonError)
