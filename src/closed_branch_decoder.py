import numpy as np
from branch import Branch, Cluster, Closed_branches


class CB_decoder():
    
    def __init__(
        self,
        pcm: np.array,
        priors: np.array,
        min_prob: float = 1e-20,
        ) -> None:
        
        self.cluster = Cluster(self)
        self.pcm = pcm
        self.m, self.n = self.pcm.shape
        self.priors = priors
        # This dual list will help indicate separations
        # self.dual_list = np.full((2, self.m), -1, dtype=int)
        self.checks = np.zeros(self.m, dtype = bool)
        
        max_number_rows = 0
        
        for column in range(self.n):
            a = len(np.where(self.pcm[:,column] == 1)[0])
            if a > max_number_rows:
                max_number_rows = a
        
        # Constructing the reduced matrix
        self.reduced_matrix = np.full((self.n, a), -1, dtype=int) # Filas son self.n Columnas son los valores no triviales.
        
        for i in range(self.n):
            non_trivial_values = np.where(self.pcm[:,i] == 1)[0]
            self.reduced_matrix[i,:len(non_trivial_values)] = non_trivial_values
        
    def update_probabilities(self,
                             priors:np.array) -> None:
        # TODO Check that this works
        self.priors = priors
    
    def sort_priors(
        self
    ):
        # This function sorts the indices of the probabilities from largest to lowest.
        return np.argsort(self.priors)[::-1]
    
    def check_if_growing(self, 
                         column: int,
                         syndrome: np.array,
                         cluster: Cluster,
                         prior: float,
                         destructive: bool = False,
                         cts_numb: int = 1) -> list:
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
        
        # TODO need to contemplate all instances. What if growth is destructive?
        
        cts = [] # Checks to search
        check_array_cluster = np.zeros(self.m, dtype=bool)
        
        for check in checks_to_consider:
            if check == -1:
                break
            elif syndrome[check] and not self.check_array[check]:
                # Check is closed
                check_array_cluster[check] = True
            
            elif syndrome[check] and self.check_array[check]:
                # Check is non-trivial in syndrome but trivial for cluster 
                # TODO, apply exception for destructive case, where the cluster to which the check belongs to is broken.
                cts.append(check)
            
            elif not syndrome[check]:
                cts.append(check)
        
        
        if len(cts) == 0:
            # Branch is closed
            # TODO change the cluster, return empty list. Perhaps cluster should be method.
            pass
        
        elif len(cts) != cts_numb:
            # Reject branch instance.
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
                self.H, # pcm
                syndrome, # syndrome
                check_array_cluster, # checks included in the branch
                branch_events, # events
                prior, # weight of the branch
                linked_list, # linked_list
                self.cluster
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
    
    def decode(self,
               syndrome,
               priors):
        
        # We order the columns according to the checks to search they have.
        ordered_columns = self.reorder_H_cts(syndrome)
        
        # We create the cluster
        self.cluster = Cluster(self)
        
        for index in self.n:
            column = self.priors[ordered_columns[index]]
            
            branch = self.check_if_growing(column, priors[column])
            
            if len(branch) == 0:
                # When initial branch is either closed or does not satisfy the growing condition.
                continue
            
            
            