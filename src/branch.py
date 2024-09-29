import numpy as np
# from closed_branch_decoder import CB_decoder
import copy

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
                 myDecoder):
        self.checks = np.zeros(myDecoder.m, dtype = bool)
        self.events = np.zeros(myDecoder.n, dtype = bool)
        self.destroyable_closed_branches: list = []
    
    def introduce_closed_branch(self,
                                events : np.array,
                                checks: np.array,
                                dest : bool = True):
        self.events = np.logical_xor(self.events, events)
        self.checks =  np.logical_xor(self.checks, checks)
        if not dest: # dest es que la rama cerrada sea destructora (que no se pueda destruir)
            cb = Closed_branches(events, checks)
            self.destroyable_closed_branches.append(cb)
            
    def destroy_cb(self, indices: list):
        indices_sorted = indices.sort(reverse = True)
        for idx in indices_sorted:
            self.events = np.logical_xor(self.events, self.destroyable_closed_branches[idx].events)
            self.checks =  np.logical_xor(self.checks, self.destroyable_closed_branches[idx].checks)
            del self.destroyable_closed_branches[idx]
            
            

class Branch:
    def __init__(self,
                #  H: np.array,
                decoder,
                 syndrome: np.array,
                 checks: np.array,
                 events : np.array,
                 check_to_search: int,
                 weight_to_consider: float,
                 linked_list: np.array,
                 nsep: int,
                 dest: bool = False,
                 cb_to_destroy: list = [], # List with the indices of the closed-branches that will be destroyed.
                 ):
        self.decoder = decoder # It is in the reduced form
        self.syndrome = syndrome
        self.checks = checks
        self.events = events
        self.check_to_search = check_to_search
        self.weight = weight_to_consider
        self.linked_list = linked_list
        self.nsep = nsep
        self.dest = dest # destructive growth, if it is True, it can destroy additional events.
        self.cb_to_destroy = cb_to_destroy
    
    def orient_growth(self) -> list:
        adjacent_events = np.where(self.decoder.reduced_matrix_transpose[self.check_to_search,:])[0]
        ad_ev = []
        for adjacent_event in adjacent_events:
            if adjacent_event == -1:
                # All cases have been considered.
                break
            if self.events[adjacent_event]:
                # If the event has been considered for this branch instance it is omitted.
                continue 
            ad_ev.append(adjacent_event)
        return ad_ev
            # Si el evento interactual con algo del cluster se solapan ramas.
                
    def grow(self) -> list:
        
        branches = []
        
        adjacent_events = self.orient_growth()
        
        for adjacent_event in adjacent_events:
            
            weight_to_consider = self.weight*self.priors[adjacent_event]
            if weight_to_consider < self.decoder.min_weight:
                continue
            events = self.events.copy()
            events[adjacent_event] = True
            checks = self.checks.copy()
            if self.dest:
                cb_to_destroy = copy.deepcopy(self.cb_to_destroy)
            else:
                cb_to_destroy = self.cb_to_destroy
            linked_list = self.linked_list.copy()
            n_sep = self.nsep
            
            # If the event has not yet been considered. We look at its other adjacent checks:
            adjacent_checks = np.where(self.decoder.reduced_matrix[adjacent_event,:])[0]
            
            
            cts = [] # These are the checks to search for this particular event.
            
            
            for adjacent_check in adjacent_checks:
                if adjacent_check == self.check_to_search:
                    # We are focusing on the shared check, must be omitted.
                    continue
                
                if self.syndrome[adjacent_check]:
                    # If it is a non-trivial syndrome we face different scenarios
                    
                    # If it is included in the branch instance, it must now be considered as a trivial check.
                    if self.checks[adjacent_check]:
                        # Consider as a trivial check.
                        if linked_list[2*adjacent_check] != -1:
                            left_value = linked_list[2*adjacent_check]
                            right_value = linked_list[2*adjacent_check+1]
                            linked_list[2*left_value+1] = right_value
                            linked_list[2*right_value] = left_value
                            linked_list[2*adjacent_check] = -1
                            linked_list[2*adjacent_check+1] = -1
                            n_sep -= 1
                        else:
                            cts.append(adjacent_check)
                            n_sep += 1
                        
                    
                    
                    # If it is included in the cluster, it has been included for another closed branch.
                    elif self.cluster.checks[adjacent_check]:
                        # If it is in the cluster three scenarios can happen:
                        
                        # 1. The branch growth is not destructive, we consider such check as trivial:
                        if not self.dest:
                            # Checking if trivial check closes any loop
                            if linked_list[2*adjacent_check] != -1:
                                left_value = linked_list[2*adjacent_check]
                                right_value = linked_list[2*adjacent_check+1]
                                linked_list[2*left_value+1] = right_value
                                linked_list[2*right_value] = left_value
                                linked_list[2*adjacent_check] = -1
                                linked_list[2*adjacent_check+1] = -1
                                n_sep -= 1
                            # Trivial check does not close a loop
                            else:
                                cts.append(adjacent_check)
                                n_sep += 1
                        else:
                            condition = False
                            # 2. If it is included as a part of a previously destroyed cb, we can consider it as non-trivial:
                            for cb_index in self.cb_to_destroy:
                                if self.cluster.cb_to_destroy[cb_index].checks[adjacent_check]:
                                    checks[adjacent_check] = True
                                    condition = True
                                    break
                                    
                            
                            # 3. The branch growth is destructive and the closed branch including the non-trivial check is not-destructive.
                            #           We destroy the branch by including it as a destructive branch.
                            if not condition:
                                for index, destroyable_cb in enumerate(self.cluster.destroyable_closed_branches):
                                    if destroyable_cb.checks[adjacent_check]:
                                        cb_to_destroy.append(index)
                                        checks[adjacent_check] = True
                                        condition = True
                                        break
                        
                            if not condition:
                                # 4. If the check does not correspond to a destructable closed branch, then it cannot be destroyed and is considered as trivial:
                                # Checking if trivial check closes any loop
                                if linked_list[2*adjacent_check] != -1:
                                    left_value = linked_list[2*adjacent_check]
                                    right_value = linked_list[2*adjacent_check+1]
                                    linked_list[2*left_value+1] = right_value
                                    linked_list[2*right_value] = left_value
                                    linked_list[2*adjacent_check] = -1
                                    linked_list[2*adjacent_check+1] = -1
                                    n_sep -= 1
                                # Trivial check does not close a loop
                                else:
                                    cts.append(adjacent_check)
                                    n_sep += 1
                        #       We consider the check as trivial.
                    
                    else:
                        # If it is a non-trivial check but it is not in the branch nor in the cluster, then it is accepted into the branch instance:
                        checks[adjacent_check] = True
                    
                else:
                    # The check is trivial syndrome[check] == 0:
                    # Checking if trivial check closes any loop
                    if linked_list[2*adjacent_check] != -1:
                        left_value = linked_list[2*adjacent_check]
                        right_value = linked_list[2*adjacent_check+1]
                        linked_list[2*left_value+1] = right_value
                        linked_list[2*right_value] = left_value
                        linked_list[2*adjacent_check] = -1
                        linked_list[2*adjacent_check+1] = -1
                        n_sep -= 1
                    else:
                        cts.append(adjacent_check)
                        n_sep += 1
                
                
            # We now generate the branch correspondent with such an event:
            og_cts = self.check_to_search
            for check_to_search in cts:
                right_v = self.linked_list[2*og_cts+1]
                linked_list[2*right_v] = check_to_search
                linked_list[2*check_to_search] = og_cts
                linked_list[2*check_to_search+1] = right_v
                linked_list[2*og_cts+1] = check_to_search
                og_cts = check_to_search
            
            if linked_list[2*self.check_to_search] == linked_list[2*self.check_to_search+1] == self.check_to_search:
                # Branch is closed
                check_to_search = -1
                assert n_sep == 0, "Error in the linked list, there should be no separations."
                branch = Branch(
                    self.decoder,
                    self.syndrome,
                    checks,
                    events,
                    check_to_search,
                    weight_to_consider,
                    linked_list,
                    n_sep,
                    dest = self.dest,
                    cb_to_destroy = cb_to_destroy
                )
                return [branch]
            
            else:
                left_value = linked_list[2*self.check_to_search]
                right_value = linked_list[2*self.check_to_search+1]
                check_to_search = right_value
                linked_list[2*left_value+1] = right_value
                linked_list[2*right_value] = left_value
                linked_list[2*self.check_to_search] = -1
                linked_list[2*self.check_to_search+1] = -1
                n_sep -= 1
                branch = Branch(
                    self.decoder,
                    self.syndrome,
                    checks,
                    events,
                    check_to_search,
                    weight_to_consider,
                    linked_list,
                    n_sep,
                    dest = self.dest,
                    cb_to_destroy = cb_to_destroy
                )
                branches.append(branch)
            # Compute    
            
            
            

        # Modify linked list accordingly:
        return branches
                
        
            
    
    