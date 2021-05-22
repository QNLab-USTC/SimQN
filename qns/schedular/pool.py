from .event import Event


class EventsPoolNode():
    def __init__(self, time_slice: int, event: Event):
        self.time_slice = time_slice
        self.event = event
        self.next: EventsPoolNode = None
        self.is_canceled = False

    def cancel(self):
        self.is_canceled = True


class EventsPool():
    '''
    A linked list for storing and processing event collections.
    This is an inner class that will not be exported.

    :param start_time_slice: the start time slice
    :param end_time_slice: the end time slice
    :var EventsPoolNode self.current: point to the current event
    :var self.current_time_slice: the start time_slice of the current event
    '''

    def __init__(self, start_time_slice: int, end_time_slice: int):
        self.start_time_slice = start_time_slice
        self.end_time_slice = end_time_slice
        self.current_time_slice = start_time_slice

        self.current: EventsPoolNode = None

    def get_current_time_slice(self) -> int:
        '''
        This function returns the start time_slice of the current event

        :return: the start time_slice of the current event
        '''
        return self.current_time_slice

    def set_current_time_slice(self, current_time_slice: int):
        '''
        This function set `self.current_time_slice`

        :param current_time_slice: the ``current`` event time_slice
        '''
        self.current_time_slice = current_time_slice

    def add_event(self, time_slice: int, event: Event) -> bool:
        '''
        This function add an event into this event pool

        :param time_slice: the ``event``'s start time_slice
        :param event: the event to insert
        :return bool: Insert event successfully or not
        '''
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
        nepn.next = p
        return True

    def remote_event(self, event):
        '''
        This function remove an event from this event pool

        :param event: the event to be removed
        '''
        p = self.current
        while p is not None:
            if p.event == event:
                p.cancel()
                return

    def get_event(self):
        '''
        This function get the current event and move ``current`` the ``current.next``

        :returns (int, event): The current ``event``'s start ``time_slice`` and the ``current`` event itself.
        '''
        p = self.current
        while p is not None and p.is_canceled:
            p = p.next
        if p is None:
            return None, None
        self.current = p.next
        self.current_time_slice = p.time_slice
        return p.time_slice, p.event

    def show_events(self):
        '''
        This function print every events after ``self.current``
        '''
        p = self.current
        while p is not None:
            print(p.time_slice, p.event)
            p = p.next
