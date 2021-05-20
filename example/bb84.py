from qns.schedular import Simulator, Protocol
from qns.log import log
from qns.bb84 import PhotonNode, OpticalFiber, PhotonRandomSendProtocol, PhotonReceiveAndMeasureProtocol, OpticalFiberProtocol

s = Simulator(0, 5, 100000)
log.set_debug(True)
log.install(s)

n1 = PhotonNode(name="n1")
sendp = PhotonRandomSendProtocol(n1, rate=10, start_time=1, end_time=5)
n1.inject_protocol(sendp)
n2 = PhotonNode(name="n2")
recvp = PhotonReceiveAndMeasureProtocol(n2)
n2.inject_protocol(recvp)
n1.install(s)
n2.install(s)

c = OpticalFiber(nodes=[n1, n2], name="c1")
ofp = OpticalFiberProtocol(c, delay=0.023, possible=0.6, rate=3, max_onfly=3)
c.inject_protocol(ofp)
c.install(s)

s.run()
