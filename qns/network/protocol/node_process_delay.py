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

from typing import Optional, Tuple, Union
from qns.entity.node.app import Application
from qns.entity.node.node import QNode
from qns.simulator.simulator import Simulator
from qns.simulator.event import Event
from qns.simulator.ts import Time


class NodeProcessDelayApp(Application):
    """
    This application will add an addition delay whenever the node received an event.
    It is used to represent the processing delay on quantum nodes.
    """
    def __init__(self, delay: float = 0, delay_event_list: Optional[Union[type, Tuple[type]]] = None):
        """

        Args:
            delay (float): the processing delay
            delay_event_list: a list of Event classic list that will add a delay.
                If `delay_event_list` is None, all events will be added a delay.
        """
        super().__init__()
        self.delay = delay
        self.delay_event_list = delay_event_list
        self.wait_rehandle_event_list = []

    def install(self, node: QNode, simulator: Simulator):
        super().install(node, simulator)

    def check_in_delay_event_list(self, event) -> bool:
        if self.delay_event_list is None:
            return True
        return isinstance(event, self.delay_event_list)

    def handle(self, node: QNode, event: Event) -> bool:
        if not self.check_in_delay_event_list(event):
            return False

        if event in self.wait_rehandle_event_list:
            self.wait_rehandle_event_list.remove(event)
            return False

        # first handle the event
        # add to list
        self.wait_rehandle_event_list.append(event)
        # get the delay time
        t = self._simulator.current_time+Time(sec=self.delay)
        # reset event's occur time
        event.t = t
        self._simulator.add_event(event)
        return True
