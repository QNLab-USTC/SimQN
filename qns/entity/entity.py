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

from qns.simulator.simulator import Simulator
from qns.simulator.event import Event


class Entity(object):
    """
    This is the basic entity class, including memories, channels and nodes.
    """

    def __init__(self, name: str = None):
        """
        Args:
            name (str): the name of this entity
        """
        self.name = name
        self._is_installed = False
        self._simulator = None

    def install(self, simulator: Simulator) -> None:
        '''
        ``install`` is called before ``simulator`` runs to initialize or set initial events

        Args:
            simulator (qns.simulator.simulator.Simulator): the simulator
        '''
        if not self._is_installed:
            self._simulator = simulator
            self._is_installed = True

    def handle(self, event: Event) -> None:
        '''
        ``handle`` is called to process an receiving ``Event``.

        Args:
            event (qns.simulator.event.Event): the event that send to this entity
        '''
        raise NotImplementedError

    def __repr__(self) -> str:
        if self.name is not None:
            return f"<entity {self.name}>"
        return super().__repr__()
