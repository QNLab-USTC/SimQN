from qns.quantum.entity.channel import QuantumChannel
from qns.schedular import Entity,Event,Simulator
from qns.schedular.entity import RecieveEvent
from qns.quantum.qubit import Polar, Qubit,Basis
import random

class Generator(Entity):
    def __init__(self, delay: float = 0,name = None):
        '''
        Generator is a sub-entity in node. It can generate new qubit

        :param name: its name
        :param delay: its delay
        '''
        super().__init__(name)
        self.delay = delay
    
    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        '''
        ''handle'' is triggered by GenerateEvent,it will use ''generate'' function to creat qubit.
        :param source: who creat the Event.
        :param event:the Event.
        '''
        self.source=source
        self.event=event
        q=self.generate(msg[0])
        
    def generate(self, polar: Polar) -> Qubit:
        '''
        ''generate''function can generate the specified type of qubit.It then will send the qubit to the source who creat the GenerateEvent.
        :param polar:the type of qubit.
        '''
        q=Qubit(self.simulator.current_time_slice+self.delay)
        q.polar=polar.value
        simulator.add_event(simulator.current_time_slice+self.delay,GenerateEvent(simulator.current_time_slice+self.delay,q))
        source.call(self.simulator,(q,),self,ReceiveEvent(self.simulator.current_time_slice))

    def __repr__(self) -> str:
        return f"<generator {self.name}> "


class Measurer(Entity):
    '''
        Measurer is a sub-entity in node. It can measure the qubit.

        :param success_prob: operation success rate 
        :param delay: its delay
        '''
    def __init__(self,delay: float = 0,name = None,success_prob:float = 1):
        super().__init__(name)
        self.delay = delay
        self.success_prob=success_prob

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self.source=source
        self.event=event
        self.measure(msg[0],msg[1],msg[2])

        
       
        
    def measure(self,qubit:Qubit,basis:Basis,error_model=None):
        '''
        ''measure''function can measure qubit.It then will send the result to the source who creat the MeasureEvent.
        :param qubit:the qubit to be measured.
        :param basis:the basis used.
        '''
        r=random.random()
        if r<=self.success_prob:
            if error_model is None:
                if qubit.polar.value == 0 or 1:
                    if basis.value == 0:
                        source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice))
                    else:
                        tmp=random.random()
                        if tmp<=0.5:
                            qubit.polar=polar.P
                            source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice))
                        else:
                            qubit.polar=polar.Q
                            source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice))
                elif qubit.polar.value == 2 or 3:
                    if basis == 1:
                        source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice))
                    else:
                        tmp=random.random()
                        if tmp<=0.5:
                            qubit.polar=polar.H
                            source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice))
                        else:
                            qubit.polar=polar.V
                            source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice))
            else:
                pass
        else:
            source.call(self.simulator,(Polar.N,),self,RecieveEvent(self.simulator.current_time_slice))
        

        







class Operator(Entity):
    '''
        Operator is a sub-entity in node. It can operate the qubit.

        :param success_prob: operation success rate 
        :param delay: its delay
        '''
    def __init__(self,delay: float = 0,name = None,success_prob:float = 1):
        super().__init__(name)
        self.delay = delay
        self.success_prob=success_prob
    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self.source=source
        self.event=event

    def notgate(self,qubit:Qubit):
        pass

        

class GenerateEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        self.qubit=qubit

    def run(self, simulator):
        print('%f 时产生了一个qbuit %s'%(self.init_time,self.qubit.name))

class MeasureEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        
class MeasureSEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        self.qubit=qubit

    def run(self, simulator):
        print('%f 时成功测量了一个qbuit %s'%(self.init_time,self.qubit.name))

class MeasureFEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        self.qubit=qubit

    def run(self, simulator):
        print('%f 时失败测量了一个qbuit %s'%(self.init_time,self.qubit.name))


class OperateEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time=init_time)
        
    def run(self, simulator):
        pass 