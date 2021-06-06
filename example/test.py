from qns.quantum.entity import Node
from qns.quantum.entity.memory import Memory,WriteEvent,ReadEvent
from qns.quantum.entity.operator import Generator,Measurer,Operator,GenerateEvent,MeasureEvent
from qns.quantum.qubit import *
from qns.schedular import *

def fun(t):
    return t[1]
s=Simulator(0,50,1000)
n1=Node('n1')
m1=Memory('m1',FilelityMode=fun)
g1=Generator(0,'g1')
mea1=Measurer(0,'mea1')
q1=Qubit(0)
q1.polar=Polar.V
n1.install(s)
m1.install(s)
g1.install(s)
mea1.install(s)
n1.add_subentity(m1)
n1.add_subentity(g1)
n1.add_subentity(mea1)

g1.call(s,(Polar.V,),n1,GenerateEvent(0),0)
mea1.call(s,(q1,Basis.X,None),n1,MeasureEvent(100),100)
s.run()