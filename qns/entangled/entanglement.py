import uuid

# entanglement between node1 and node2


class Entanglement():
    '''
    This class represents a Bell State Entangled qubits.

    :param nodes: two ``QuantumNode`` that share this entangled qubit.
    :param birth_time_slice: its birthday
    :param fidelity: its fidelity
    :param life_func: a function that decide whether it is decohered. If it is ``None``, the entanglement will be immortal.
    :param name: its name
    '''

    def __init__(self, nodes, birth_time_slice: int,
                 fidelity: int = 1, life_func=None, name=None):
        self.nodes = nodes
        self.birth_time_slice = birth_time_slice
        self.fidelity = fidelity
        if life_func is None:
            self.life_func = self._default_life_func
        else:
            self.life_func = life_func
        if name is not None:
            self.name = name
        else:
            self.name = uuid.uuid4()

    def is_alive(self):
        '''
        Check whether it is still alive
        
        :returns bool: is alive or not
        '''
        return self.life_func()

    # immoral
    def _default_life_func(self):
        return True

    def __str__(self):
        return "<ent {} {}, fidelity: {}>".format(self.name, self.nodes, self.fidelity)

    def __repr__(self):
        return "<ent {} {}, fidelity: {}>".format(self.name, self.nodes, self.fidelity)
