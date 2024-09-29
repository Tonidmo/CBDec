import numpy as np
from branch import Branch, Cluster, Closed_branches


class CB_decoder():
    
    def __init__(
        self,
        pcm: np.array,
        priors: np.array,
        min_weight: float = 1e-20,
        max_num_branches: int = 25,
        cts_max: int = 3
        ) -> None:
        
        self.cluster = Cluster(self)
        self.max_num_branches = max_num_branches
        self.pcm = pcm
        self.cts_max = cts_max
        self.m, self.n = self.pcm.shape
        self.priors = priors
        self.min_weight = min_weight
        # This dual list will help indicate separations
        # self.dual_list = np.full((2, self.m), -1, dtype=int)
        self.checks = np.zeros(self.m, dtype = bool)
        
        
        max_number_rows = 0
        
        for column in range(self.n):
            a = len(np.where(self.pcm[:,column] == 1)[0])
            if a > max_number_rows:
                max_number_rows = a
        
        # Constructing the reduced matrix
        
        self.reduced_matrix = np.full((self.n, max_number_rows), -1, dtype=int) # Filas son self.n Columnas son los valores no triviales.
        
        for i in range(self.n):
            non_trivial_values = np.where(self.pcm[:,i] == 1)[0]
            self.reduced_matrix[i,:len(non_trivial_values)] = non_trivial_values
        
        # Constructing the reduced matrix but for the checks.
        
        max_number_columns = 0
        
        for row in range(self.m):
            a = len(np.where(self.pcm[row, :] == 1)[0])
            if a > max_number_columns:
                max_number_columns = a
        
        self.reduced_matrix_transpose = np.full((self.m, max_number_columns), -1, dtype=int) # Filas son self.n Columnas son los valores no triviales.
        
        for i in range(self.m):
            non_trivial_values = np.where(self.pcm[i,:] == 1)[0]
            self.reduced_matrix_transpose[i,:len(non_trivial_values)] = non_trivial_values  
            
        
    def update_probabilities(self,
                             priors:np.array) -> None:
        self.priors = priors
    
    def sort_priors(
        self
    ):
        # This function sorts the indices of the probabilities from largest to lowest.
        return np.argsort(self.priors)[::-1]
    
    def check_if_growing(self, 
                         column: int,
                         syndrome: np.array,
                         destructive: bool = False) -> list:
        """_summary_
        This method checks if the column is a branch instance. 
            If it is a closed branch, returns a closed branch.
            If it is a branch instance, it returns a list with a single Branch which can grow.
            If it is not a branch instance or a closed branch, returns empty list.
        Args:
            column (int): _description_
            syndrome (np.array): _description_
            destructive (bool, optional): _description_. Defaults to False.
            cts_numb (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """

        
        
        checks_to_consider = self.reduced_matrix[column,:]
        
        
        cts = [] # Checks to search
        checks = np.zeros(self.m, dtype=bool)
        cb_to_destroy = []
        
        
        for check in checks_to_consider:
            if check == -1:
                break
            elif syndrome[check] and not self.check_array[check]:
                # Check is closed
                checks[check] = True
                condition = True
            
            elif syndrome[check] and self.check_array[check]:
                # Check is non-trivial in syndrome but trivial for cluster 
                if destructive:
                    broken = False
                    for index, destroyable_cb in enumerate(self.cluster.destroyable_closed_branches):
                        # If it finds a cb to break, it breaks it.
                        if destroyable_cb.checks[check]:
                                cb_to_destroy.append(index)
                                checks[check] = True
                                condition = True
                                broken = True
                                break
                    if not broken:
                        cts.append(check)
                else:
                    cts.append(check)
            
            elif not syndrome[check]:
                cts.append(check)
        
        if not condition:
            # If the column does not contain any adjacent non-trivial check, it is omitted.
            return []
        nsep = len(cts)
        if nsep == 0:
            # Branch is closed, include closed-branch, return empty list.
            self.cluster.destroy_cb(cb_to_destroy)
            events = np.zeros(self.n, dtype = bool)
            events[column] = True
            self.cluster.introduce_closed_branch(
                    events,
                    checks,
                    dest= destructive
                )
            return []
        
        elif nsep > self.cts_max:
            # Reject branch instance because it includes too many open checks.
            return []
        
        else:
            branch_events = np.zeros(self.n, dtype = bool)
            branch_events[column] = True
            linked_list = np.full(2*self.m, -1, dtype = int)
            for i in range(len(cts)):
                check_slot_left = 2*cts[i]
                check_left = (i-1)
                linked_list[check_slot_left] = cts[check_left]
                check_slot_right = (2*cts[i])+1
                check_right = (i+1) % len(cts)
                linked_list[check_slot_right] = cts[check_right]
            
            branch = Branch(
                self,
                syndrome, # syndrome
                checks, # checks included in the branch
                branch_events, # events
                cts[-1], # check_to_search,
                self.priors[column],# weight to consider
                linked_list, # linked_list
                len(cts),
                dest = destructive,
                cb_to_destroy=cb_to_destroy
            )
            return [branch]

    
    def reorder_H_cts(self, syndrome):
        cts_per_columns = np.zeros(self.n, dtype = np.int8)
        for column in range(self.n):
            checks_to_consider = self.reduced_matrix[column,:]
            cts = 0
            for check in checks_to_consider:
                if check == -1:
                    break
                elif not syndrome[check]:
                    cts += 1
            cts_per_columns[column] = cts
        
        ordered_columns = np.argsort(cts_per_columns)
        
        return ordered_columns, cts_per_columns
    
    def grow_round(self,
                   ordered_columns:np.array,
                   dest: bool) -> None:
        for index in range(self.n):
            # Non destructive growth.
            column = self.priors[ordered_columns[index]]
            
            # This way we avoid destruction branches replacing completely equal non-destruction ones.
            if self.cluster.events[column]:
                continue
            
            branches = self.check_if_growing(column,
                                             destructive = dest
                                             )
            
            
            if len(branches) == 0:
                # When initial branch is either closed or does not satisfy the growing condition we proceed to the following.
                continue
            
            
            # while (len(branches) < self.max_branches) and (len(branches) != 0):
            while (len(branches) != 0):
                new_branches = []
                for branch in branches:
                    new_branches += branch.grow()
                
                branches = []
                min_nsep = float('inf') 
                for branch in new_branches:
                    if branch.nsep < min_nsep:
                        min_nsep = branch.nsep
                        branches = [branch]
                    elif branch.nsep == min_nsep:
                        branches.append(branch)
                if min_nsep == 0:
                    branches = [branches[0]]
                    break
                if len(branches) > self.max_num_branches:
                    branches = []
                    break
            if len(branches) == 0:
                continue
            
            closed_branch = branches[0]
            self.cluster.destroy_cb(closed_branch.nsep)
            events = closed_branch.events
            checks = closed_branch.checks
            
            self.cluster.introduce_closed_branch(
                    events,
                    checks,
                    dest= dest
                )

                #TODO check when len(branches) == 1, it is closed. Just pick first one and look nsep value.    
    
    
    def decode(self,
               syndrome: np.array):
        
        # We order the columns according to the checks to search they have.
        ordered_columns = self.reorder_H_cts(syndrome)
        
        # We create the cluster
        self.cluster = Cluster(self)
        
        # Non-destructible growth
        self.grow_round(
            ordered_columns,
            dest = False)
        
        # Destructible growth
        self.grow_round(
            ordered_columns,
            dest = True)
        
        return self.cluster.events, self.cluster.checks
        
        
        
            
                    
            
            
            