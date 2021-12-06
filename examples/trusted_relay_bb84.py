from qns.network.topology.topo import ClassicTopology
from qns.simulator.simulator import Simulator
from qns.network import QuantumNetwork
from qns.network.topology import LineTopology
from qns.network.protocol.bb84 import BB84RecvApp, BB84SendApp

import numpy as np

light_speed = 299791458
total_length = 100000


def drop_rate(length):
    # drop 0.2 db/KM
    return 1 - np.exp(- length / 50000)


for num in [2, 3, 4, 5, 6]:
    results = []
    for i in range(10):
        length = total_length / (num - 1)
        s = Simulator(0, 10, accuracy=10000000000)
    
        topo = LineTopology(num, nodes_apps=[], qchannel_args={
                            "delay": length / light_speed, 
                            "drop_rate": drop_rate(length)},
                            cchannel_args={"delay": length / light_speed})
    
        net = QuantumNetwork(topo = topo, classic_topo= ClassicTopology.Follow)
    
        rps = []
        for qchannel in net.qchannels:
            (src, dst) = qchannel.node_list
            cchannel = None
            for c in net.cchannels:
                if c.name == f"c-{qchannel.name}":
                    cchannel = c
            assert(cchannel is not None)
    
            sp = BB84SendApp(dst, qchannel, cchannel, send_rate=1000)
            rp = BB84RecvApp(src, qchannel, cchannel)
            src.add_apps(sp)
            dst.add_apps(rp)
            rps.append(rp)
    
        for n in net.nodes:
            n.install(s)
        s.run()
        rets = [len(rp.succ_key_pool) / 10 for rp in rps]
        results.append(min(rets))
    print(num, np.mean(results), np.std(results))