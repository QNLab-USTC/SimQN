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

from typing import Dict, List, Optional

from qns.entity.node.node import QNode
from qns.entity.node.app import Application
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.qchannel.remote_qchannel import RemoteQuantumChannel
from qns.entity.cchannel.cchannel import ClassicChannel
from qns.entity.cchannel.remote_cchannel import RemoteClassicChannel
from qns.simulator.MPIsimulator import MPISimulator


class SubnetManager:
    """
    Manages a subnet assigned to one MPI process.

    Given the full topology and a partition mapping, this class:
    - Stores all nodes (remote ones as data references, not installed)
    - Installs only the nodes owned by this MPI rank
    - For intra-process channels: installs the existing channel on the simulator
    - For cross-process channels: replaces the original channel with a
      RemoteChannel on the local node

    Usage::

        topo = GridTopology(nodes_number=9, ...)
        nl, ql = topo.build()           # built identically on all processes
        cl = topo.add_cchannels(...)    # classic channels

        partition = ManualPartitioner({"n0": 0, "n1": 1, ...}).partition(nl)

        mgr = SubnetManager(nl, ql, cl, partition, rank, sim)
        mgr.add_app("n1", MyApp())
        sim.run()
    """

    def __init__(self,
                 nodes: List[QNode],
                 qchannels: List[QuantumChannel],
                 cchannels: List[ClassicChannel],
                 partition: Dict[str, int],
                 rank: int,
                 simulator: MPISimulator):
        self.rank = rank
        self.sim = simulator
        self.partition = partition

        self.nodes: Dict[str, QNode] = {}
        self.qchannels: List[QuantumChannel] = []
        self.cchannels: List[ClassicChannel] = []
        self._channel_map: dict = {}  

        self._build(nodes, qchannels, cchannels)

    def _build(self,
               nodes: List[QNode],
               qchannels: List[QuantumChannel],
               cchannels: List[ClassicChannel]):

        for node in nodes:
            self.nodes[node.name] = node
            self.sim.register_entity(node)

        for qch in qchannels:
            self._install_one_channel(qch, self.qchannels)

        for cch in cchannels:
            self._install_one_channel(cch, self.cchannels)

        for node in nodes:
            if self.partition.get(node.name, 0) == self.rank:
                node.install(self.sim)

    def _install_one_channel(self, channel, channel_list):
        """Determine if a channel is intra-process or cross-process."""
        owners = {self.partition.get(n.name, 0) for n in channel.node_list}

        if len(owners) <= 1:
            self._install_regular(channel, channel_list)
        else:
            self._install_remote(channel, channel_list)

    def _install_regular(self, channel, channel_list):
        """An intra-process channel: just install it on the simulator."""
        self.sim.register_entity(channel)
        channel.install(self.sim)
        channel_list.append(channel)
        self._channel_map[channel] = channel

    def _install_remote(self, original, channel_list):
        """
        A cross-process channel: replace the original channel with a RemoteChannel
        on each locally-owned node.
        """
        remote_rank = next(
            self.partition.get(n.name, 0) for n in original.node_list
            if self.partition.get(n.name, 0) != self.rank
        )

        if isinstance(original, QuantumChannel):
            remote_ch: QuantumChannel = RemoteQuantumChannel(
                dest_rank=remote_rank,
                name=original.name,
                fidelity=original.fidelity,
                bandwidth=original.bandwidth,
                delay=original.delay_model,
                drop_rate=original.drop_rate,
                max_buffer_size=original.max_buffer_size,
                length=original.length,
                decoherence_rate=original.decoherence_rate,
                transfer_error_model_args=original.transfer_error_model_args,
            )
        else:
            remote_ch = RemoteClassicChannel(
                dest_rank=remote_rank,
                name=original.name,
                bandwidth=original.bandwidth,
                delay=original.delay_model,
                drop_rate=original.drop_rate,
                max_buffer_size=original.max_buffer_size,
                length=original.length,
            )

        remote_ch.install(self.sim)
        self.sim.register_entity(remote_ch)
        self._channel_map[original] = remote_ch

        seen = set()
        for n in original.node_list:
            if n.name in seen:
                continue
            seen.add(n.name)

            node_obj = self.nodes.get(n.name)
            if node_obj is None:
                continue

            remote_ch.node_list.append(node_obj)

            if self.partition.get(n.name, 0) == self.rank:
                if isinstance(original, QuantumChannel):
                    if original in node_obj.qchannels:
                        node_obj.qchannels.remove(original)
                    node_obj.qchannels.append(remote_ch)
                else:
                    if original in node_obj.cchannels:
                        node_obj.cchannels.remove(original)
                    node_obj.cchannels.append(remote_ch)

        channel_list.append(remote_ch)

    def get_node(self, name: str) -> Optional[QNode]:
        """Get any node by name, including remote nodes (as data references)."""
        return self.nodes.get(name)

    def resolve_channel(self, channel):
        """
        Return the installed channel for the given original channel.

        For intra-process channels this returns the same channel;
        for cross-process channels it returns the RemoteChannel replacement.

        """
        return self._channel_map.get(channel, channel)

    def add_app(self, node_name: str, app: Application):
        """Add an application to a node owned by this process."""
        node = self.nodes.get(node_name)
        if node is not None and self.partition.get(node_name, -1) == self.rank:
            node.add_apps(app)
            app.install(node, self.sim)