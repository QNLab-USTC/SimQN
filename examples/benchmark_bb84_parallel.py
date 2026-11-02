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

"""
BB84 parallel speedup benchmark.

Serial mode (no MPI):
    python examples/benchmark_bb84_parallel.py

Parallel mode (with MPI):
    mpiexec -n 2 python examples/benchmark_bb84_parallel.py --parallel
    mpiexec -n 4 python examples/benchmark_bb84_parallel.py --parallel

The script builds a line topology of N nodes, runs BB84 on each adjacent
link, and reports wall-clock time.  The speedup is:

    speedup = serial_time / parallel_max_time
"""

import time
import argparse
import sys
import numpy as np

from qns.entity.cchannel.cchannel import ClassicChannel
from qns.entity.qchannel.qchannel import QuantumChannel
from qns.entity.node.node import QNode
from qns.simulator.simulator import Simulator
from qns.network.protocol.bb84 import BB84RecvApp, BB84SendApp, KEY_BLOCK_SIZE
from qns.utils.rnd import set_seed

LIGHT_SPEED = 299791458        
LINK_LENGTH = 500_00      
SIM_TIME = 10.0                
SEND_RATE = 1000            
ACCURACY = 10_000_000_000     
LOOKAHEAD = 0.00015            
DEFAULT_NODES = 8              
DEFAULT_SEED = 42              

def drop_rate(length: float) -> float:
    """Drop rate for a fibre of given length (0.2 dB/km → exponential)."""
    return 1 - np.exp(-length / 50000)



def _build_line(num_nodes: int):
    delay = LINK_LENGTH / LIGHT_SPEED
    dr = drop_rate(LINK_LENGTH)

    nodes = [QNode(f"n{i}") for i in range(1, num_nodes + 1)]
    qlinks = []
    clinks = []
    for i in range(num_nodes - 1):
        qlink = QuantumChannel(name=f"l{i+1}", delay=delay, drop_rate=dr, bandwidth=0)
        clink = ClassicChannel(name=f"c{i+1}", delay=delay)
        nodes[i].add_qchannel(qlink)
        nodes[i + 1].add_qchannel(qlink)
        nodes[i].add_cchannel(clink)
        nodes[i + 1].add_cchannel(clink)
        qlinks.append(qlink)
        clinks.append(clink)
    return nodes, qlinks, clinks


def _add_bb84_apps_direct(nodes, qlinks, clinks, send_rate):
    """Add BB84 send/recv apps directly (serial path, no SubnetManager)."""
    for i in range(len(nodes) - 1):
        sp = BB84SendApp(nodes[i + 1], qlinks[i], clinks[i], send_rate=send_rate)
        rp = BB84RecvApp(nodes[i], qlinks[i], clinks[i])
        nodes[i].add_apps(sp)
        nodes[i + 1].add_apps(rp)


def run_serial(num_nodes: int, send_rate: int = SEND_RATE, seed: int = DEFAULT_SEED):
    set_seed(seed)
    nodes, qlinks, clinks = _build_line(num_nodes)
    _add_bb84_apps_direct(nodes, qlinks, clinks, send_rate)

    sim = Simulator(0, SIM_TIME, accuracy=ACCURACY)
    for n in nodes:
        n.install(sim)

    t0 = time.time()
    sim.run()
    wall_time = time.time() - t0

    total_keys = sum(
        len(app.key_pool) * KEY_BLOCK_SIZE
        for n in nodes
        for app in n.apps
        if isinstance(app, BB84SendApp)
    )
    total_events = sim.total_events

    print(f"[SERIAL]  nodes={num_nodes:>2}  "
          f"time_used={wall_time:>8.3f} s  "
          f"events={total_events:>8}  "
          f"key_bits={total_keys:>6}")
    return wall_time, total_keys, total_events



def run_parallel(num_nodes: int, send_rate: int = SEND_RATE, seed: int = DEFAULT_SEED):
    from mpi4py import MPI
    from qns.simulator.MPIsimulator import MPISimulator
    from qns.network.partition import ManualPartitioner, SubnetManager

    set_seed(seed)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()


    nodes, qlinks, clinks = _build_line(num_nodes)


    mapping = {}
    per_rank = (num_nodes + size - 1) // size
    for i in range(num_nodes):
        mapping[f"n{i+1}"] = min(i // per_rank, size - 1)
    partition = ManualPartitioner(mapping).partition(nodes, size)


    sim = MPISimulator(comm=comm, end_second=SIM_TIME,
                       accuracy=ACCURACY, lookahead=LOOKAHEAD)
    mgr = SubnetManager(nodes, qlinks, clinks, partition, rank, sim)


    for i in range(num_nodes - 1):
        src_name = f"n{i+1}"
        dst_name = f"n{i+2}"
        qch = mgr.resolve_channel(qlinks[i])
        cch = mgr.resolve_channel(clinks[i])

        sp = BB84SendApp(mgr.get_node(dst_name), qch, cch, send_rate=send_rate)
        rp = BB84RecvApp(mgr.get_node(src_name), qch, cch)
        mgr.add_app(src_name, sp)
        mgr.add_app(dst_name, rp)
            
        

    t0 = time.time()
    sim.run()
    wall_time = time.time() - t0

    local_keys = 0
    for name, node in mgr.nodes.items():
        if partition.get(name, -1) == rank:
            for app in node.apps:
                if isinstance(app, BB84SendApp):
                    local_keys += len(app.key_pool) * KEY_BLOCK_SIZE
    local_events = sim.total_events

    all_times = comm.gather(wall_time, root=0)
    all_keys = comm.reduce(local_keys, op=MPI.SUM, root=0)
    all_events = comm.reduce(local_events, op=MPI.SUM, root=0)

    if rank == 0:
        max_time = max(all_times) if all_times else wall_time
        print(f"[PARALLEL] ranks={size:>2}  nodes={num_nodes:>2}  "
              f"wall(max)={max_time:>8.3f} s  "
              f"events={all_events:>8}  "
              f"key_bits={all_keys:>6}")
        print(f"           time_used(per rank): {', '.join(f'{t:.3f}' for t in (all_times or [wall_time]))}")
        return max_time, all_keys, all_events
    return None, None, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BB84 parallel speedup benchmark")
    parser.add_argument("--parallel", action="store_true",
                        help="run with MPI (use mpiexec)")
    parser.add_argument("--nodes", type=int, default=DEFAULT_NODES,
                        help=f"number of nodes in line topology (default: {DEFAULT_NODES})")
    parser.add_argument("--send-rate", type=int, default=SEND_RATE,
                        help=f"qubits/sec per link (default: {SEND_RATE})")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"random seed (default: {DEFAULT_SEED})")
    args = parser.parse_args()

    if args.parallel:
        result = run_parallel(args.nodes, args.send_rate, args.seed)
    else:
        serial_time, serial_keys, serial_events = run_serial(args.nodes, args.send_rate, args.seed)
        print()
        print("To run the parallel version:")
        print(f"  mpiexec -n 2 python {sys.argv[0]} --parallel --nodes {args.nodes}")
        print(f"  mpiexec -n 4 python {sys.argv[0]} --parallel --nodes {args.nodes}")
        print()
        print("Speedup = serial_wall_time / parallel_max_wall_time")