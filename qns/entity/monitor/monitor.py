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

import pandas as pd
from typing import Any, Callable, Optional
from qns.entity.entity import Entity
from qns.network.network import QuantumNetwork
from qns.simulator.event import Event
from qns.simulator.simulator import Simulator
from qns.simulator.ts import Time


class MonitorEvent(Event):
    """
    the event that notify the monitor to write down network status
    """
    def __init__(self, t: Optional[Time], monitor,
                 name: Optional[str] = None, by: Optional[Any] = None):
        super().__init__(t, name, by)
        self.monitor = monitor

    def invoke(self) -> None:
        self.monitor.handle(self)


class Monitor(Entity):
    def __init__(self, name: Optional[str] = None, network: Optional[QuantumNetwork] = None) -> None:
        """
        Monitor is a virtual entity that helps users to collect network status.

        Args:
            name (str): the monitor's name
            network (Optional[QuantumNetwork]): a optional parameter, the quantum network.
        """
        super().__init__(name=name)
        self.network = network
        self.data: pd.DataFrame = pd.DataFrame()

        self.attributions = []

        self.watch_at_time = False
        self.watch_at_start = False
        self.watch_at_finish = False
        self.watch_period = []
        self.watch_event = []

    def install(self, simulator: Simulator) -> None:
        super().install(simulator=simulator)
        if self.watch_at_start or self.watch_at_finish or len(self.watch_period) > 0:
            self.watch_at_time = True

        if self.watch_at_start:
            event = MonitorEvent(t=self._simulator.ts, monitor=self, name="start watch event", by=self)
            self._simulator.add_event(event)
        if self.watch_at_finish:
            event = MonitorEvent(t=self._simulator.te, monitor=self, name="finish watch event", by=self)
            self._simulator.add_event(event)
        for p in self.watch_period:
            tp = Time(sec=p)
            t = self._simulator.ts
            while t <= self._simulator.te:
                t = t + tp
                event = MonitorEvent(t=t, monitor=self, name=f"period watch event({p})", by=self)
                self._simulator.add_event(event)

        for event_type in self.watch_event:
            try:
                self._simulator.watch_event[event_type].append(self)
            except (IndexError, KeyError, ValueError):
                self._simulator.watch_event[event_type] = [self]

    def handle(self, event: Event) -> None:
        self.calculate_date(event)

    def calculate_date(self, event: Event):
        current_time = self._simulator.tc.sec
        record = {"time": current_time}
        for (name, calculate_func) in self.attributions:
            record[name] = [calculate_func(self._simulator, self.network, event)]
        record_pd = pd.DataFrame(record)
        self.data = pd.concat([self.data, record_pd], ignore_index=True)

    def get_date(self):
        """
        Get the collected data.

        Returns:
            the collected data, as a ``pd.DataFrame``.
        """
        return self.data

    def add_attribution(self, name: str,
                        calculate_func: Callable[[Simulator, Optional[QuantumNetwork], Optional[Event]], Any]) -> None:
        """
        Set an attribution that will be recorded. For example, an attribution could be the throughput, or the fidelity.

        Args:
            name (str): the column's name, e.g., fidelity, throughput, time ...
            calculate_func (Callable[[Simulator, Optional[QuantumNetwork], Optional[Event]]):
                a function to calculate the value, it has three input parameters (Simulator, QuantumNetwork, Event),
                and it returns the value.

        Usage:
            m = Monitor()

            # record the event happening time
            m.add_attribution("time", lambda s,n,e: e.t)

            # get the 'name' attribution of the last node
            m.add_attribution("count", lambda s,network,e: network.nodes[-1].name)
        """
        self.attributions.append((name, calculate_func))

    def at_start(self) -> None:
        """
        Watch the initial status before the simulation starts.

        Usage:
            m.at_start()
        """
        self.watch_at_start = True

    def at_finish(self) -> None:
        """
        Watch the final status after the simulation.

        Usage:
            m.at_finish()
        """
        self.watch_at_finish = True

    def at_period(self, period_time: float) -> None:
        """
        Watch network status at a constant period.

        Args:
            period_time (float): the period of watching network status [s]

        Usage:
            # record network status every 3 seconds.
            m.at_period(3)
        """
        assert(period_time > 0)
        self.watch_period.append(period_time)

    def at_event(self, event_type) -> None:
        """
        Watch network status whenever the event happends

        Args:
            event_type (Event): the watching event

        Usage:
            # record network status when a node receives a qubit
            m.at_event(RecvQubitPacket)
        """
        self.watch_event.append(event_type)
