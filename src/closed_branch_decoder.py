import numpy as np



class CB_decoder():
    
    def __init__(
        self,
        pcm: np.array,
        priors: np.array,
        min_prob: float = 1e-20,
        ) -> None:
        
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
    
    def check_if_growing(self, column, syndrome):
        # This method checks if the column is a branch instance.
        checks_to_consider = self.reduced_matrix[column,:]
        
        # TODO need to contemplate all instances. What if growth is destructive?
        for check in checks_to_consider:
            if self.check_array[check] == 1:
                pass
            
            elif syndrome(check) == 1 and self.check_array[check] == 0:
                # Check is closed
                pass
            
    
    def decode(self,
               syndrome):
        
        for index in self.n:
            column = self.priors[index]
            