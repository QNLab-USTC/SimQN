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

from typing import Callable, Dict, List, Tuple, Union

from qns.entity.node.node import QNode
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.cchannel.cchannel import ClassicChannel
from qns.network.route.route import RouteImpl, NetworkRouteError


class DijkstraRouteAlgorithm(RouteImpl):
    """
    This is the dijkstra route algorithm implement
    """

    def __init__(self, name: str = "dijkstra",
                 metric_func: Callable[[Union[QuantumChannel, ClassicChannel]], float] = None) -> None:
        """
        Args:
            name: the routing algorithm's name
            metric_func: the function that returns the metric for each channel.
                The default is the const function m(l)=1
        """
        self.name = name
        self.route_table = {}
        if metric_func is None:
            self.metric_func = lambda _: 1
        else:
            self.metric_func = metric_func

    def build(self, nodes: List[QNode], channels: List[Union[QuantumChannel, ClassicChannel]]):
        INF = 999999

        for n in nodes:
            selected = []
            unselected = [u for u in nodes]

            d = {}
            for nn in nodes:
                if nn == n:
                    d[n] = [0, []]
                else:
                    d[nn] = [INF, [nn]]

            while len(unselected) != 0:
                ms = unselected[0]
                mi = d[ms][0]

                for s in unselected:
                    if d[s][0] < mi:
                        ms = s
                        mi = d[s][0]

                # d[ms] = [d[ms][0], d[ms][1]]
                selected.append(ms)
                unselected.remove(ms)

                for link in channels:
                    if ms not in link.node_list:
                        continue
                    if len(link.node_list) < 2:
                        raise NetworkRouteError("broken link")
                    idx = link.node_list.index(ms)
                    idx_s = 1 - idx
                    s = link.node_list[idx_s]
                    if s in unselected and d[s][0] > d[ms][0] + self.metric_func(link):
                        d[s] = [d[ms][0] + self.metric_func(link), [ms] + d[ms][1]]

            for nn in nodes:
                d[nn][1] = [nn] + d[nn][1]
            self.route_table[n] = d

    def query(self, src: QNode, dest: QNode) -> List[Tuple[float, QNode, List[QNode]]]:
        """
        query the metric, nexthop and the path

        Args:
            src: the source node
            dest: the destination node

        Returns:
            A list of route paths. The result should be sortted by the priority.
            The element is a tuple containing: metric, the next-hop and the whole path.
        """
        ls: Dict[QNode, List[float, List[QNode]]] = self.route_table.get(src, None)
        if ls is None:
            return []
        le = ls.get(dest, None)
        if le is None:
            return []
        try:
            metric = le[0]
            path: List[QNode] = le[1]
            path = path.copy()
            path.reverse()
            if len(path) <= 1:
                next_hop = None
            else:
                next_hop = path[1]
                return [(metric, next_hop, path)]
        except Exception:
            return []
