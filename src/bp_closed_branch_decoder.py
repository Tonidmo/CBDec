# Imports
import numpy as np
from ldpc import bp_decoder

# We begin for a model for data qubit noise. Later, we will expand it to a detector error model type of decoder.
class BP_CB_decoder():
    
    def __init__(
        self,
        pcm: np.array,
        error_rate: np.array,
        max_branches: int = 25,
        max_growths: int = 5,
        max_cts: int = 3,
        max_bp_iters: int = 30,
        bp_method: str = "product_sum",
        ) -> None:
        
        self.pcm = pcm
        self.error_rate = error_rate
        self.max_branches = max_branches
        self.max_growths = max_growths
        self.checks_to_search = max_cts
        self.max_bp_iters = max_bp_iters
        self.bp_method = bp_method
        
        self.bp_decoder = bp_decoder(
            self.pcm,
            error_rate = self.error_rate,
            max_iter = self.max_bp_iters,
            bp_method = self.bp_method
        )
        
        self.m, self.n = self.pcm.shape
        
        
        
        
        def decode(self, syndrome):
            # Attempt BP
            
            recovered_error = self.bp_decoder.decode(syndrome)
            
            if self.bp_decoder.converge:
                return recovered_error
            
            # If not, compute the weights and begin cb.
            llrs = self.log_prob_ratios
            
            ps = 1/(1+np.exp(llrs))
            eps = 1e-14
            
            ps[ps > 1-eps] = 1-eps
            ps[ps < eps] = eps
            
            # TODO Establish a weight convention
            for column in range(self.n):
                pass        
        
    
    