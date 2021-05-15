from .event import Event

class EventsPoolNode():
    def __init__(self, time_slice: int, event: Event):
        self.time_slice = time_slice
        self.event = event
        self.next: EventsPoolNode = None
        self.is_canceled = False
    
    def cancel(self):
        self.is_canceled = True


# EventsPool: Linked List of Events Pool
class EventsPool():
    def __init__(self, start_time_slice: int, end_time_slice: int):
        self.start_time_slice = start_time_slice
        self.end_time_slice= end_time_slice
        self.current_time_slice = start_time_slice

        self.head: EventsPoolNode = EventsPoolNode(-1, None) # head node
        self.current: EventsPoolNode = self.head

    def get_current_time_slice(self):
        return self.current_time_slice
    
    def set_current_time_slice(self, current_time_slice: int):
        self.current_time_slice = current_time_slice

    def add_event(self,time_slice: int, event: Event):
        if time_slice < self.current_time_slice or time_slice > self.end_time_slice:
            return False
        
        nepn = EventsPoolNode(time_slice, event)
        
        if self.current is None:
            self.current = nepn
            return True

        if nepn.time_slice < self.current.time_slice:
            nepn.next = self.current
            self.current = nepn
            return True

        p = self.current
        q = self.current
        while p is not None and p.time_slice <= nepn.time_slice:
            q = p
            p = p.next
        q.next = nepn
        nepn.next =p
        if self.current == self.head:
            self.current = self.head.next
        return True
    
    def remote_event(self, event):
        p = self.current
        while p is not None:
            if p.event == event:
                p.cancel()
                return
        
    def get_event(self):
        p = self.current
        while p is not None and p.is_canceled:
            p = p.next
        if p is None:
            return None, None
        self.current = p.next
        self.current_time_slice = p.time_slice
        return p.time_slice, p.event

    def show_events(self):
        p = self.current
        while p is not None:
            print(p.time_slice, p.event)
            p = p.next

        
        


