import numpy as np
from closed_branch_decoder import CB_decoder


class Closed_branches:
    def __init__(self,
                 events: np.array,
                 checks: np.array):
        self.events = events
        self.checks = checks
    
    def add_closed_branches(self,
                            cb2):
        self.events = np.logical_xor(self.events, cb2.events)
        self.checks = np.logical_xor(self.checks, cb2.checks)
        

class Cluster:
    def __init__(self,
                 myDecoder: CB_decoder):
        self.checks = np.zeros(myDecoder.m, dtype = bool)
        self.events = np.zeros(myDecoder.n, dtype = bool)
        self.dest_closed_branches: list = []
    
    def introduce_closed_branch(self,
                                events : np.array,
                                checks: np.array,
                                dest : bool = True):
        self.events = np.logical_xor(self.events, events)
        self.checks =  np.logical_xor(self.checks, checks)
        if dest: # dest es que la rama cerrada es destruible
            cb = Closed_branches(events, checks)
            self.dest_closed_branches.append(cb)
            
            

class Branch:
    def __init__(self,
                 H: np.array,
                 syndrome: np.array,
                 checks: np.array,
                 events : np.array,
                 check_to_search: int,
                 weight_to_consider: float,
                 linked_list: np.array,
                 # separations: np.array,  TODO creo que no hace falta esta lista de separaciones, que con linked_list ya estamos.
                 # sep_int: int, TODO como en searations
                 cluster: Cluster,
                 dest: bool = False,
                 cb_to_destroy: Closed_branches = Closed_branches(np.zeros(1, dtype=bool),np.zeros(1, dtype=bool))):
        pass
            
    
    