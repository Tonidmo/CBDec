# Imports
import numpy as np
from ldpc import bp_decoder
from closed_branch_decoder import CB_decoder

# We begin for a model for data qubit noise. Later, we will expand it to a detector error model type of decoder.
class BP_CB_decoder():
    
    def __init__(
        self,
        pcm: np.array,
        channel_probs: np.array,
        max_branches: int = 25,
        max_growths: int = 5,
        max_cts: int = 3,
        max_bp_iters: int = 30,
        bp_method: str = "product_sum",        
        min_weight: float = 1e-20,
        max_num_branches: int = 25,
        cts_max: int = 3
        ) -> None:
        
        self.pcm = pcm
        self.channel_probs = channel_probs
        self.max_branches = max_branches
        self.max_growths = max_growths
        self.checks_to_search = max_cts
        self.max_bp_iters = max_bp_iters
        self.bp_method = bp_method
        
        # Maybe change the error rate for channel probabilities
        
        self.bp_decoder = bp_decoder(
            self.pcm,
            channel_probs = self.channel_probs,
            max_iter = self.max_bp_iters,
            bp_method = self.bp_method
        )
        
        self.cb_decoder = CB_decoder(
            self.pcm,
            channel_probs,
            min_weight = min_weight,
            max_num_branches=max_num_branches,
            cts_max = cts_max
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
            
            self.cb_decoder.update_probabilities(ps)
            
            # TODO Check if error converges with syndrome
            
            recovered_error, recovered_checks = self.cb_decoder.decode(syndrome)
            
            return recovered_error
        
    
    