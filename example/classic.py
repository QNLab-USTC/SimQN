from qns.schedular import Simulator, Event, Entity
from qns.quantum import ClassicSender, ClassicReceiver, ClassicP2PChannel, ClassicRepeater

s = Simulator(0, 10, 100000)

n1 = ClassicSender(5,8,1,"hello")
n1.install(s)

n2 = ClassicRepeater(delay = 0.5)
n2.install(s)

n3 = ClassicReceiver()
n3.install(s)

l1 = ClassicP2PChannel(n1, n2, 1, 0.3)
l1.install(s)

l2 = ClassicP2PChannel(n2, n3, 1, 0.3)
l2.install(s)

s.run()