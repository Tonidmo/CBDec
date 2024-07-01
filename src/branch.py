import numpy as np
import copy



class Closed_Branch:
    """
    Closed branch class which is composed by two boolean vectors:
    
    checks (boolean length-m np.array): syndrome that produces the specific closed branch.
    events (boolean length-m np.array): representing the closed_branch error.
    
    """
    def __init__(
            self,
            checks : np.array,
            events : np.array
    ):
        self.checks = checks
        self.events = events


class Cluster:
    """
    A cluster consists on the already considered closed branches and helps branches grow.
    
    - checks (boolean length-m np.array): syndrome that produces the set of closed branches considered in the cluster.
    
    - events (boolean length-n np.array): events considered by the set of closed branches.
    
    - check_cluster (int length m,2 matrix): for each check, the first column indicates if the closed branch which has it is 
    non destructible (0) or destructible (1), if it is destructible the second column indicates the index of the branch it belongs to
    in the closed_branches_dest list.
    
    - syndrome (bool length m np.array): the syndrome that is being decoded.
    
    - closed_branches_dest (list): list of Closed_Branch elements which have been obtained growing destructively.
    
    - closed_branches_non_dest (list): list of Closed_Branch elements which have been obtained growing non-destructively.
    
    """
    def __init__(
            self,
            checks : np.array, # Inputs necesarios para ver el tamaño del código.
            events : np.array,
            check_cluster: np.array,
            syndrome: np.array,
            closed_branches_dest : list = [],
            closed_branches_non_dest : list = [],
    ):
        self.checks = checks
        self.events = events
        self.check_cluster = check_cluster
        self.syndrome = syndrome
        self.closed_branches_dest = closed_branches_dest
        self.closed_branches_non_dest = closed_branches_non_dest

    def check_if_valid(self, check: int, dest : bool = False) -> bool:
        if self.syndrome[check] and not self.checks[check]:
            # Si no 
            return True
        if self.syndrome[check] and self.checks[check]:
            if dest and self.check_cluster[check,0] == 1:
                # Branch growth is destructive and will destroy closed branch with the check.
                self.destroy_closed_branch(self, self.check_cluster[check,1])
                self.check_cluster[check,0] == 1
                return True
            else:
                # Branch growth is not destructive or the check belongs to a destructive closed branch.
                return False
        else:
            return False

    def destroy_closed_branch(self, index : int):
        self.checks = np.bitwise_xor(self.checks, self.closed_branches_non_dest[index].checks)
        self.events = np.bitwise_xor(self.events, self.closed_branches_non_dest[index].events)
        self.closed_branches_non_dest[index] = None
    
    def add_closed_branch(self, cb: Closed_Branch, dest : bool = False):
        self.checks = np.bitwise_xor(self.checks, cb.checks)
        self.events = np.bitwise_xor(self.events, cb.events)
        checks = np.where(cb.checks == 1)[0]
        if dest:
            self.check_cluster[checks, 0] = 1
            self.closed_branches_dest.append(cb)
        else:
            self.closed_branches_non_dest.append(cb)
            self.check_cluster[checks, 0] = 0
            self.check_cluster[checks, 1] = len(self.closed_branches_non_dest)-1

class Branch:
    """
    A Branch is a branch instance which will grow towards the code until it is closed. 
    
    The atributes are:
    
    - Hred (int np.array): which indicates the location of the non trivial elements for each column of the pcm.
    
    - checks (boolean length-m np.array): syndrome that produces the set of closed branches considered in the cluster.
    
    - events (boolean length-n np.array): events considered by the set of closed branches.
    
    - check_cluster (int length m,2 matrix): for each check, the first column indicates if the closed branch which has it is 
    non destructible (0) or destructible (1), if it is destructible the second column indicates the index of the branch it belongs to
    in the closed_branches_dest list.
    
    - syndrome (bool length m np.array): the syndrome that is being decoded.
    
    - closed_branches_dest (list): list of Closed_Branch elements which have been obtained growing destructively.
    
    - closed_branches_non_dest (list): list of Closed_Branch elements which have been obtained growing non-destructively.
    
    """
    def __init__(
        self,
        Hcol : np.array,
        Hrows : np.array,
        checks : np.array,
        events : np.array,
        check_to_search: int,
        weight: float,
        linked_list : np.array,
        separations : int,
        sep_array : np.array,
        cluster : Cluster,
        destructive: bool = False
    ):
        self.Hcol = Hcol
        self.Hrow = Hrows
        self.checks = checks
        self.events = events
        self.check_to_search = check_to_search
        self.weight = weight
        self.linked_list = linked_list
        self.separations = separations
        self.sep_array = sep_array
        self.Cluster = cluster
        self.destructive = destructive
        
    def grow_branch(self):
        """
        ESQUEMA
        
        TODO FALTA CLONAR CLUSTERS
        
        1 Buscar columnas adyacentes al check to search.
        
        columnas_adyacentes = self.Hrows[self.check_to_search,:]
        
        
        for column in columnas_adyacentes:
            if column == -1:
                break
            if column in self.events:
                continue
            if self.events[column]:
                continue
            rows_a_proponer = self.Hcols[column,:]
            for row_a_proponer in rows_a_proponer:
                new_cluster = copy.deepcopy(self.cluster)
                if not new_cluster.check_if_valid(row_a_proponer):
                    
            
        # Solo nos quedaremos con los clusters de mínimo número de separaciones.
        
        """
        pass
        
        
    
