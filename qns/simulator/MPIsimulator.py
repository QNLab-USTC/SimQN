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

import time
from typing import Optional, Type, Dict, Any
from qns.simulator.ts import Time, default_accuracy
from qns.simulator.event import Event
from qns.simulator.pool import DefaultEventPool
import qns.utils.log as log
from . import ts
from collections import deque
from mpi4py import MPI

default_start_second = 0.0
default_end_second = 60.0
default_lookahead = 0.01

class MPISimulator(object):
    """
    The discrete-event driven parallel simulator core
    This simulator is used in an MPI environment with a conservative synchronization algorithm.
    """
    def __init__(self, 
                 comm: MPI.Comm,
                 start_second: float = default_start_second,
                 end_second: float = default_end_second,
                 accuracy: int = default_accuracy,
                 pool_cls: Type[DefaultEventPool] = DefaultEventPool,
                 pool_kwargs: Optional[Dict[str, Any]] = None,
                 lookahead: float = default_lookahead) -> None:
        """
        Args:
            comm (MPI.Comm): the MPI communicator
            start_second (float): the start second of the simulation
            end_second (float): the end second of the simulation
            accuracy (int): the number of time slots per second
            pool_cls (Type[DefaultEventPool]): the event pool class
            pool_kwargs (Optional[Dict[str, Any]]): the keyword arguments for event pool
            lookahead (float): the lookahead time
        """
        self.accuracy = comm.bcast(accuracy, root=0)  
        ts.default_accuracy = self.accuracy           

        self.ts: Time = self.time(sec=start_second)
        self.te: Time = self.time(sec=end_second)

        self.event_pool = pool_cls(self.ts, self.te, **(pool_kwargs or {}))
        self.status = {}
        self.total_events = 0

        self.watch_event = {}
        
        self.time_spend: float =0.0 
        self.global_min_time: Time = self.ts
        self.lookahead: Time = self.time(sec=lookahead)
        self.sync_time: Time = min(self.global_min_time+lookahead,self.te)
        self.comm = comm                  
        self.rank = comm.Get_rank()       
        self.size = comm.Get_size()       
        self.InQ: deque[Event] = deque()
        self.OutQ: deque[Event] = deque()
        self.local_time: Time = self.ts
        self._entity_registry: Dict[str, object] = {}

    def register_entity(self, entity) -> None:
        """Register an entity by its name for cross-process event remapping."""
        if entity.name is not None:
            self._entity_registry[entity.name] = entity

    def _remap_event(self, event: Event) -> None:
        """Remap remote entity references in a received event to local entities."""
        if not self._entity_registry:
            return
        for attr_name in ('by', 'dest'):
            if hasattr(event, attr_name):
                obj = getattr(event, attr_name)
                if obj is not None and hasattr(obj, 'name') and obj.name is not None:
                    local = self._entity_registry.get(obj.name)
                    if local is not None:
                        setattr(event, attr_name, local)

    @property
    def local_min_time(self) -> Time:
        '''
        Get the local_min_time of the simulator

        Returns:
            (Time) the current time of the simulator, which is the local_min_time of the simulator
        '''
        if self.OutQ and self.event_pool.event_list:
            valid_ts = [e.t for e in self.OutQ if e.t is not None]
            if valid_ts:
                return min(self.event_pool.min_time, min(valid_ts))
        if not self.OutQ and self.event_pool.event_list:
            return self.event_pool.min_time
        if self.OutQ and not self.event_pool.event_list:
            valid_ts = [e.t for e in self.OutQ if e.t is not None]
            if valid_ts:
                return min(valid_ts)
        if not self.OutQ and not self.event_pool.event_list:
            return self.local_time
    @property
    def current_time(self) -> Time:
        '''
        Get the current time of the simulation

        Returns:
            (Time) the current time
        '''
        return self.local_time
    
    @property
    def tc(self) -> Time:
        """
        The alias of `current_time`
        """
        return self.current_time

    def time(self, time_slot: Optional[int] = None, sec: Optional[float] = None) -> Time:
        """
        Produce a ``Time`` using ``time_slot`` or ``sec``

        Args:
            time_slot (Optional[int]): the time slot
            sec (Optional[float]): the second
        Returns:
            the produced ``Time`` object
        """
        if time_slot is not None:
            return Time(time_slot=time_slot, accuracy=self.accuracy)
        return Time(sec=sec, accuracy=self.accuracy)

    def add_event(self, event: Event) -> None:
        '''
        Add an ``event`` into simulator event pool.
        :param event: the inserting event
        '''
        if self.event_pool.add_event(event):
            self.total_events += 1

    def run(self) -> None:
        '''
        Run the parallel simulation
        '''
        log.debug("simulation started.")

        trs = time.time()

        while self.local_time < self.te:
            #Communicating phase
            local_slot = self.local_min_time.time_slot              
            global_slot = self.comm.allreduce(local_slot, op=MPI.MIN)  
            self.global_min_time = Time(time_slot=global_slot)    
            self.sync_time = min(self.global_min_time+self.lookahead,self.te)
            
            send_bufs: dict[int, list[Event]] = {}
            for event in self.OutQ:
                dest = event.dest_rank
                if dest is None or dest == self.rank:
                    self.event_pool.add_event(event)   
                else:
                    send_bufs.setdefault(dest, []).append(event)
            my_counts = [len(send_bufs.get(r, [])) for r in range(self.size)]
            all_counts = self.comm.allgather(my_counts)
            
            sends = []
            for dest, events in send_bufs.items():
                for event in events:
                    req = self.comm.isend(event, dest=dest, tag=0)
                    sends.append(req)
                    
            recvs = []
            for src in range(self.size):
                if src == self.rank:
                    continue
                count = all_counts[src][self.rank] 
                for _ in range(count):
                    req = self.comm.irecv(source=src, tag=0)
                    recvs.append(req)
                    
            for req in sends:
                req.wait()           
            for req in recvs:
                event = req.wait()   
                self.InQ.append(event)
            self.OutQ.clear()
            for event in self.InQ:
                self._remap_event(event)
                self.add_event(event)
            self.InQ.clear()
            if self.global_min_time >= self.te:
                break
            #computing phase
            while True:
                event = self.event_pool.next_event()
                if event is None:
                    break
                if event.t >= self.sync_time:
                    self.event_pool.add_event(event)       
                    break
                self.local_time = event.t                  
                if event.is_canceled:
                    continue
                event.invoke()                             
                monitor_list = self.watch_event.get(event.__class__, [])
                for m in monitor_list:
                    m.handle(event)
            self.local_time = self.sync_time
            self.event_pool.tc = self.local_time
            #notify_global_QSM_about_synchronization()

        tre = time.time()
        self.time_spend = tre - trs
        log.debug("simulation finished.")

        if tre - trs == 0:
            log.debug(f"runtime {tre - trs}, {self.total_events} events,\
                sim_time {self.te.sec - self.ts.sec}, xINF")
        else:
            log.debug(f"runtime {tre - trs}, {self.total_events} events,\
                sim_time {self.te.sec - self.ts.sec}, x{(self.te.sec - self.ts.sec)/(tre-trs)}")