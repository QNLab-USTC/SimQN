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

from typing import Callable, List, Optional, Tuple

from qns.simulator.simulator import Simulator
from qns.simulator import Event


class Application(object):
    """
    Application can be deployed on the quantum nodes.
    """
    def __init__(self):
        self._simulator = None
        self._node = None
        self._dispatch_dict: List[Tuple[List, List, Callable]] = []

    def install(self, node, simulator: Simulator):
        """
        install initial events for this QNode

        Args:
            node (QNode): the node that will handle this event
            simulator (Simulator): the simulator
        """
        self._simulator = simulator
        self._node = node

    def handle(self, node, event: Event) -> Optional[bool]:
        """
        process the event on the node.

        Args:
            node (QNode): the node that will handle this event
            event (Event): the event

        Return:
            skip (bool, None): if skip is True, further applications will not handle this event
        """
        return self._dispatch(node, event)

    def _dispatch(self, node, event: Event) -> Optional[bool]:
        for elem in self._dispatch_dict:
            eventTypeList = elem[0]
            byList = elem[1]
            handler = elem[2]

            flag_et = False
            flag_by = False
            if len(eventTypeList) > 0:
                for et in eventTypeList:
                    if isinstance(event, et):
                        flag_et = True
            else:
                flag_et = True

            if len(byList) == 0 or event.by in byList:
                flag_by = True

            if flag_et and flag_by:
                skip = handler(node, event)
                if skip is True:
                    return skip
        return False

    def add_handler(self, handler, EventTypeList: List = [], ByList: List = []):
        """
        Add a handler function to the dispather.

        Args:
            handler: The handler to process the event.
                It is an object method whose function signature is the same to ``handle`` function.
            EventTypeList: a list of Event Class Type. An empty list meaning to match all events.
            ByList: a list of Entities, QNodes or Applications, that generates this event.
                An empty list meaning to match all entities.
        """
        elem = (EventTypeList, ByList, handler)
        self._dispatch_dict.append(elem)

    def get_node(self):
        """
        get the node that runs this application

        Returns:
            the quantum node
        """
        return self._node

    def get_simulator(self):
        """
        get the simulator

        Returns:
            the simulator
        """
        return self._simulator
