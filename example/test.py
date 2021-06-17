from qns.quantum.entity import Node
from qns.quantum.entity.memory import Memory,WriteEvent,ReadEvent
from qns.quantum.entity.operator import Generator,Measurer,Operator,GenerateEvent,MeasureEvent
from qns.quantum.qubit import *
from qns.schedular import *
from qns.quantum.protocol.recievepro import Recievepro

s=Simulator(0,50,1000)
n1=Node('n1')
o1=Operator(30,'o1')
m1=Memory('m1',FilelityMode=o1.time_decay)
g1=Generator(60,name='g1')
mea1=Measurer(300,'mea1')
q1=Qubit(20)
q1.polar=Polar.V


n1.inject_protocol(Recievepro(n1))

n1.install(s)
m1.install(s)
g1.install(s)
o1.install(s)
mea1.install(s)
n1.add_subentity(m1)
n1.add_subentity(g1)
n1.add_subentity(mea1)

g1.call(s,(Polar.V,),n1,GenerateEvent(0),0)
m1.call(s,(q1,0),n1,WriteEvent(50),50)
m1.call(s,(0,),n1,ReadEvent(60),69)
mea1.call(s,(q1,Basis.Z,None),n1,MeasureEvent(100),100)
s.run()