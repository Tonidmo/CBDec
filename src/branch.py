import numpy as np
# from closed_branch_decoder import CB_decoder
import copy

class Closed_branches:
    def __init__(self,
                 events: np.array,
                 checks: np.array,
                 weight: float ):
        self.events = events
        self.checks = checks
        self.weight = weight
        self.support = np.sum(self.events)
    # def add_closed_branches(self,
    #                         cb2):
    #     self.events = np.logical_xor(self.events, cb2.events)
    #     self.checks = np.logical_xor(self.checks, cb2.checks)
        
        

class Cluster:
    def __init__(self,
                 myDecoder):
        self.checks = np.zeros(myDecoder.m, dtype = bool)
        self.events = np.zeros(myDecoder.n, dtype = bool)
        self.destroyable_closed_branches: list = []
        self.cluster_weight: list = []
        self.support: list = []
    
    def introduce_closed_branch(self,
                                events : np.array, # n-boolean array of events in closed branch, 
                                checks: np.array, # m-boolean array of non-trivial checks in closed branch
                                weight: float, # probability product of events support 
                                dest : bool = True): # Whether the growth was destructive or not
        
        self.events = np.logical_xor(self.events, events) # Updated events
        self.checks =  np.logical_xor(self.checks, checks) # Updated checks
        self.cluster_weight.append(weight) # Weight list
        self.support.append(np.sum(events)) # Event support list
        if not dest: # If it is a non-destroyable branch, it is added to the destroyable_closed_branches list.
            cb = Closed_branches(events, checks, weight)
            self.destroyable_closed_branches.append(cb)
            
    def destroy_cb(self, indices: list):
        indices.sort(reverse = True)
        for idx in indices:
            self.events = np.logical_xor(self.events, self.destroyable_closed_branches[idx].events)
            self.checks =  np.logical_xor(self.checks, self.destroyable_closed_branches[idx].checks)
            ### TODELETE ###
            condition = False
            for weight, index in enumerate(self.cluster_weight):
                if weight == self.destroyable_closed_branches[idx].events:
                    condition = True
                    break
            assert condition
            assert self.support[index] == np.sum(self.destroyable_closed_branches[index].events) 
            del self.separate_branch_weight[index]
            del self.support[index]
            ##############
            del self.destroyable_closed_branches[idx]
            
            

class Branch:
    def __init__(self,
                #  H: np.array,
                decoder,
                 syndrome: np.array,
                 checks: np.array, # length-m boolean array containing non-trivial checks of the branch instance
                 events : np.array, # length-n boolean array containing non-trivial events of the branch instance
                 check_to_search: int, # Trivial check which will be grown upon in the following grow iteration
                 weight_to_consider: float, # Probability product of the support of the events for the branch instance
                 linked_list: np.array, 
                 nsep: int, # Number of separations, trivial checks yet to be closed
                 dest: bool = False, # Whether the growth is destructive or not.
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
        # In the future, use csc, csr format for reduced_matrix.
        adjacent_events = self.decoder.reduced_matrix_transpose[self.check_to_search]
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
        
        # List of adjacent events to the check to grow. Possible directions the branch instance can follow.
        adjacent_events = self.orient_growth()
        
        

        for adjacent_event in adjacent_events:
            
            # Combined support probability considering the adjacent event
            weight_to_consider = self.weight*self.decoder.priors[adjacent_event]
            if weight_to_consider < self.decoder.min_weight:
                # If the weight is lower than the minimum weight, adjacent event is discarded.
                continue
            
            # If it is a valid direction, we produce the attributes of the future branch
            events = self.events.copy()
            events[adjacent_event] = True
            checks = self.checks.copy()
            if self.dest:
                cb_to_destroy = copy.deepcopy(self.cb_to_destroy)
            else:
                cb_to_destroy = self.cb_to_destroy
            linked_list = self.linked_list.copy()
            n_sep = self.nsep
            assert n_sep >= 0, "Error in the linked list, there should be no separations."
            
            
            # We consider the adjacent checks 
            adjacent_checks = self.decoder.reduced_matrix[adjacent_event]
            
            
            cts = [] # These are the checks to search for this particular event.
            
            
            for adjacent_check in adjacent_checks:
                if adjacent_check == self.check_to_search:
                    # The check to search is omitted as a future direction.
                    continue
                
                if adjacent_check == -1:
                    # Whenever we hit a -1, the reduced matrix indicates there are no more adjacent_checks.
                    break
                
                if self.syndrome[adjacent_check]:
                    # If it is a non-trivial syndrome we face different scenarios
                    
                    # If it is included in the branch instance, it must now be considered as a trivial check.
                    if self.checks[adjacent_check]:
                        # Consider as a trivial check.
                        if linked_list[2*adjacent_check] != -1:
                            # A loop has been produced, where two trivial checks close one with another. therefore, we can reduce the number of separations.
                            left_value = linked_list[2*adjacent_check]
                            right_value = linked_list[2*adjacent_check+1]
                            linked_list[2*left_value+1] = right_value
                            linked_list[2*right_value] = left_value
                            linked_list[2*adjacent_check] = -1
                            linked_list[2*adjacent_check+1] = -1
                            n_sep -= 1
                            assert n_sep >= 0, "Error in the linked list, there should be no separations."
                        else:
                            # A trivial check is included and, therefore, an additional separation.
                            cts.append(adjacent_check)
                            n_sep += 1
                            assert n_sep >= 0, "Error in the linked list, there should be no separations."
                        
                    
                    
                    # If it is included in the cluster, it has been included for another closed branch.
                    elif self.decoder.cluster.checks[adjacent_check]:
                        # If it is in the cluster several scenarios can happen:
                        
                        # 1. The branch growth is not destructive, we consider such check as trivial:
                        if not self.dest:
                            # Checking if trivial check closes any loop
                            if linked_list[2*adjacent_check] != -1:
                                # A loop has been produced, where two trivial checks close one with another. 
                                # Therefore, we can reduce the number of separations.
                                left_value = linked_list[2*adjacent_check]
                                right_value = linked_list[2*adjacent_check+1]
                                linked_list[2*left_value+1] = right_value
                                linked_list[2*right_value] = left_value
                                linked_list[2*adjacent_check] = -1
                                linked_list[2*adjacent_check+1] = -1
                                n_sep -= 1
                            # Trivial check does not close a loop
                            else:
                                # A trivial check is included and, therefore, an additional separation.
                                cts.append(adjacent_check)
                                n_sep += 1
                                assert n_sep >= 0, "Error in the linked list, there should be no separations."
                        else:
                            condition = False
                            if len(cb_to_destroy)> 0:
                                # 2. If it is included as a part of a previously destroyed cb, we can consider it as non-trivial:
                                for cb_index in cb_to_destroy:
                                    if self.decoder.cluster.destroyable_closed_branches[cb_index].checks[adjacent_check]:
                                        checks[adjacent_check] = True
                                        condition = True
                                        break
                                    
                            
                            # 3. The branch growth is destructive and the closed branch including the non-trivial check is non-destructive.
                            #           We destroy the branch by including it as a destructive branch.
                            if not condition and len(self.decoder.cluster.destroyable_closed_branches)> 1:
                                for index, destroyable_cb in enumerate(self.decoder.cluster.destroyable_closed_branches):
                                    if destroyable_cb.checks[adjacent_check]:
                                        assert index not in cb_to_destroy
                                        checks[adjacent_check] = True
                                        condition = True
                                        cb_to_destroy.append(index)
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
                                    assert n_sep >= 0, "Error in the linked list, there should be no separations."
                                # Trivial check does not close a loop
                                else:
                                    cts.append(adjacent_check)
                                    n_sep += 1
                                    assert n_sep >= 0, "Error in the linked list, there should be no separations."
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
                        assert n_sep >= 0, "Error in the linked list, there should be no separations."
                    else:
                        cts.append(adjacent_check)
                        n_sep += 1
                        assert n_sep >= 0, "Error in the linked list, there should be no separations."
                
                
            # We now generate the branch correspondent with such an event:
            og_cts = self.check_to_search
            
            # If there are trivial checks_to_search in the new column that has been included, we include them in the linked_list.
            if len(cts) > 0:
                linked_list[2*cts[-1]+1] = linked_list[2*og_cts+1]
                linked_list[2*(linked_list[2*og_cts+1])] = cts[-1]
            for check_to_search in cts:
                linked_list[2*check_to_search] = og_cts
                linked_list[2*og_cts+1] = check_to_search
                og_cts = check_to_search
            


            # Now that we have finished the process, we remove the self.check_to_search from  the linked_list.
            left_value = linked_list[2*self.check_to_search]
            right_value = linked_list[2*self.check_to_search+1]
            check_to_search = right_value
            n_sep -= 1
            linked_list[2*left_value+1] = right_value
            linked_list[2*right_value] = left_value
            linked_list[2*self.check_to_search] = -1
            linked_list[2*self.check_to_search+1] = -1
            

            if n_sep == 0:
                # Branch is closed
                check_to_search = -1
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
            
            # Else, branch can continue to grow, generate branch and place it in the branches list.
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
            # Store allt eh branches in this list
            
            
            

        # Modify linked list accordingly:
        return branches
                
        
            
    
    