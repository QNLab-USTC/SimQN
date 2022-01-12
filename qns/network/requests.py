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

from typing import Dict


class Request():
    """
    A request is a source-destination pair represents a quantum transmitting request.
    """

    def __init__(self, src, dest, attr: Dict = {}) -> None:
        """
        Args:
            src: the source node
            dest: the destination node
            attr: other attributions
        """
        from qns.entity import QNode
        self.src: QNode = src
        self.dest: QNode = dest
        self.attr: Dict = attr

    def __repr__(self) -> str:
        return f"<Request {self.src}->{self.dest}>"
