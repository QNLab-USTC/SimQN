from qns.schedular import Simulator, Event, Entity
from qns.quantum import ClassicSender, ClassicReceiver, ClassicP2PChannel, ClassicRepeater

s = Simulator(0, 10, 100)

n1 = ClassicSender(5,8,1,"hello")
n2 = ClassicRepeater(0.4)
n3 = ClassicReceiver()

l1 = ClassicP2PChannel(n1, n2, 0.4, 0.3)
l1.install(s)
l2 = ClassicP2PChannel(n2, n3, 0.4, 0.3)
l2.install(s)

n1.install(s)
n2.install(s)
n3.install(s)

s.run()