from qns.quantum.entity.channel import QuantumChannel
from qns.schedular import Entity,Event,Simulator
from qns.schedular.entity import RecieveEvent
from qns.quantum.qubit import Polar, Qubit,Basis
import random

class Generator(Entity):
    def __init__(self, delay: float = 0, fidelity = 1,name = None):
        '''
        Generator is a sub-entity in node. It can generate new qubit

        :param name: its name
        :param delay: its delay
        '''
        super().__init__(name)
        self.delay = delay
        self.fidelity = fidelity
    
    def install(self, simulator: Simulator):
        self.simulator = simulator

    
    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        '''
        
        '''
        pass
    
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
<<<<<<< HEAD
        Generate a new qubit with certain fidelity and polar

        :param: the polarization of this qubit
        :returns: the newly generated qubit
        '''
        e = Qubit(self.simulator.current_time_slice, fidelity = self.fidelity, live_func = None)
        e.set_polar(polar)
        return e
=======
        ''generate''function can generate the specified type of qubit.It then will send the qubit to the source who creat the GenerateEvent.
        :param polar:the type of qubit.
        '''
        q=Qubit(self.simulator.current_time_slice+self.delay)
        q.polar=polar.value
        self.simulator.add_event(self.simulator.current_time_slice+self.delay,GenerateSEvent(self.simulator.current_time_slice+self.delay,q))
        self.source.call(self.simulator,(q,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
>>>>>>> c6c3c3e65888782cbee5ec32295ea605035bc241

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
                        self.simulator.add_event(self.simulator.current_time_slice+self.delay,MeasureSEvent(self.simulator.current_time_slice+self.delay,qubit))
                        self.source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
                    else:
                        tmp=random.random()
                        if tmp<=0.5:
                            qubit.polar=Polar.P
                            self.simulator.add_event(self.simulator.current_time_slice+self.delay,MeasureSEvent(self.simulator.current_time_slice+self.delay,qubit))
                            self.source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
                        else:
                            qubit.polar=Polar.Q
                            self.simulator.add_event(self.simulator.current_time_slice+self.delay,MeasureSEvent(self.simulator.current_time_slice+self.delay,qubit))
                            self.source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
                elif qubit.polar.value == 2 or 3:
                    if basis == 1:
                        self.simulator.add_event(self.simulator.current_time_slice+self.delay,MeasureSEvent(self.simulator.current_time_slice+self.delay,qubit))
                        self.source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
                    else:
                        tmp=random.random()
                        if tmp<=0.5:
                            qubit.polar=Polar.H
                            self.simulator.add_event(self.simulator.current_time_slice+self.delay,MeasureSEvent(self.simulator.current_time_slice+self.delay,qubit))
                            self.source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
                        else:
                            qubit.polar=Polar.V
                            self.simulator.add_event(self.simulator.current_time_slice+self.delay,MeasureSEvent(self.simulator.current_time_slice+self.delay,qubit))
                            self.source.call(self.simulator,(qubit.polar.value,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
            else:
                pass
        else:
            self.simulator.add_event(self.simulator.current_time_slice+self.delay,MeasureFEvent(self.simulator.current_time_slice+self.delay,qubit))
            self.source.call(self.simulator,(Polar.N,),self,RecieveEvent(self.simulator.current_time_slice+self.delay),self.simulator.current_time_slice+self.delay)
        

        







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

    def time_decay(self,qubit:Qubit):
        decoherence_time_slice=50
        if self.simulator.current_time_slice-qubit.birth_time_slice>=decoherence_time_slice:
            qubit.fidelity=0
        return qubit

        

class GenerateEvent(Event):
    def __init__(self,init_time):
        super().__init__(init_time)

class GenerateSEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        self.qubit=qubit

    def run(self, simulator):
        pass
        #print('%f 时产生了一个qbuit %s'%(simulator.current_time,self.qubit.name))

class GenerateFEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        self.qubit=qubit

    def run(self, simulator):
        pass

class MeasureEvent(Event):
    def __init__(self,init_time):
        super().__init__(init_time)
        
class MeasureSEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        self.qubit=qubit

    def run(self, simulator):
        pass
        #print('%f 时成功测量了一个qbuit %s'%(simulator.current_time,self.qubit.name))

class MeasureFEvent(Event):
    def __init__(self,init_time,qubit: Qubit):
        super().__init__(init_time)
        self.qubit=qubit

    def run(self, simulator):
        pass
        #print('%f 时失败测量了一个qbuit %s'%(simulator.current_time,self.qubit.name))


class OperateEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time=init_time)
        
    def run(self, simulator):
        pass 