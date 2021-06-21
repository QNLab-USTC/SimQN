from qns.schedular import Entity,Event,Simulator
from qns.schedular.entity import RecieveEvent
from qns.quantum.qubit import *

class Memory(Entity):
    '''
        Memory is a sub-entity in node. It can store and access qubit.

        :param name: its name.
        :param size: its size.
        :param FilelityMode: its FilelityMode which will decide the status of qubit when the qubit is readed.
        '''
    def __init__(self,name:str=None,size:int=-1,FilelityMode=None):
        super().__init__(name)
        self.size=size
        self.FilelityMode=FilelityMode
        self.Register=[]
        self.full=0

    def handle(self, simulator: Simulator, msg: object, source=None, event: Event = None):
        self.event=event
        self.source=source
        if type(self.event)==WriteEvent:
            self.Write(msg[0])
        elif type(self.event)==ReadEvent:
            self.Read(msg[0])
        elif type(self.event)==GetEvent:
            self.Get(msg[0])
        
    def Write(self,qubit)->bool:
        '''
        ''Write''function can store qubit in the specified location.
        :param qubit:the qubit to be stored.
        :param index:the address.
        '''
        
        if self.size== -1:
            self.Register.append(qubit)
            self.full+=1
            self.simulator.add_event(self.simulator.current_time_slice,WriteSEvent(self.simulator.current_time_slice))
            return True
        elif self.full<self.size:
            self.Register.append(qubit)
            self.full+=1
            self.simulator.add_event(self.simulator.current_time_slice,WriteSEvent(self.simulator.current_time_slice))
            return True
        else:
            self.simulator.add_event(self.simulator.current_time_slice,WriteFEvent(self.simulator.current_time_slice))
            return False

    def Read(self,t)->Qubit:
        '''
        ''Read''function can read qubit in the specified location.
        :param t:the name of qubit or the qubit itself.
        '''
        if type(t)==Qubit:
            for i in range(0,self.full):
                if self.Register[i]==t:
                    self.simulator.add_event(self.simulator.current_time_slice,ReadSEvent(self.simulator.current_time_slice))
                    self.source.call(self.simulator,(self.FilelityMode(self.Register[i]),),self,RecieveEvent(self.simulator.current_time_slice))
                    return
        
            self.simulator.add_event(self.simulator.current_time_slice,ReadFEvent(self.simulator.current_time_slice))
        else:
            for i in range(0,self.full):
                if self.Register[i].name==t:
                    self.simulator.add_event(self.simulator.current_time_slice,ReadSEvent(self.simulator.current_time_slice))
                    self.source.call(self.simulator,(self.FilelityMode(self.Register[i]),),self,RecieveEvent(self.simulator.current_time_slice))
                    return
        
            self.simulator.add_event(self.simulator.current_time_slice,ReadFEvent(self.simulator.current_time_slice))
        
        

    def Get(self,t)->Qubit:
        '''
        ''Get''function can get qubit in the specified location which will then disappear in the memory.
        :param t:the name of qubit or the qubit itself.
        '''
        if type(t)==Qubit:
            for i in range(0,self.full):
                if self.Register[i]==t:
                    self.simulator.add_event(self.simulator.current_time_slice,GetSEvent(self.simulator.current_time_slice))
                    self.source.call(self.simulator,(self.FilelityMode(self.Register[i]),),self,RecieveEvent(self.simulator.current_time_slice))
                    self.full-=1
                    del self.Register[i]
                    return
        
            self.simulator.add_event(self.simulator.current_time_slice,GetFEvent(self.simulator.current_time_slice))
        else:
            for i in range(0,self.full):
                if self.Register[i].name==t:
                    self.simulator.add_event(self.simulator.current_time_slice,GetSEvent(self.simulator.current_time_slice))
                    self.source.call(self.simulator,(self.FilelityMode(self.Register[i]),),self,RecieveEvent(self.simulator.current_time_slice))
                    self.full-=1
                    del self.Register[i]
                    return
        
            self.simulator.add_event(self.simulator.current_time_slice,GetFEvent(self.simulator.current_time_slice))
        
        

    


class WriteEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    

class WriteSEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        pass
        #print('time:%f写入成功'%simulator.current_time)

class WriteFEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        pass
        #print('time:%f写入失败'%simulator.current_time)

class ReadEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)


class ReadSEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        pass
        #print('time:%f读取成功'%simulator.current_time)

class ReadFEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        pass
        #print('time:%f读取失败'%simulator.current_time)

class GetEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)


class GetSEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        pass
        #print('time:%f读取成功'%simulator.current_time)

class GetFEvent(Event):
    def __init__(self, init_time=None):
        super().__init__(init_time)

    def run(self, simulator):
        pass
        #print('time:%f读取失败'%simulator.current_time)