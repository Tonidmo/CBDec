# Imports
import numpy as np
from ldpc import bp_decoder
from src.closed_branch_decoder import CB_decoder

# We begin for a model for data qubit noise. Later, we will expand it to a detector error model type of decoder.
class BP_CB_decoder():
    
    def __init__(
        self,
        pcm: np.array,
        channel_probs: np.array,
        max_bp_iters: int = 1000,
        bp_method: str = "product_sum",        
        min_weight: float = 1e-40,
        max_num_branches: int = 1000,
        cts_max: int = 5
        ) -> None:
        
        self.pcm = pcm
        self.channel_probs = channel_probs
        self.max_branches = max_num_branches
        self.max_bp_iters = max_bp_iters
        self.bp_method = bp_method
        self.min_weight = min_weight
        
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
            min_weight = self.min_weight,
            max_num_branches = max_num_branches,
            cts_max = cts_max
        ) 
        
        self.m, self.n = self.pcm.shape
        
        
    def update_probabilities(self, new_probs: np.array):
        self.channel_probs = new_probs        


    def decode(self, syndrome):
        self.cb_decoder.update_weight(self.min_weight)
        # Attempt BP
        recovered_error = self.bp_decoder.decode(syndrome)
        
        if self.bp_decoder.converge:
            return recovered_error
        # print('CB called')
        # If not, compute the weights and begin cb.
        llrs = self.bp_decoder.log_prob_ratios
        
        ps = 1/(1+np.exp(llrs))
        eps = 1e-14
        
        ps[ps > 1-eps] = 1-eps
        ps[ps < eps] = eps
        
        self.cb_decoder.update_probabilities(ps)
        
        
        
        recovered_error, recovered_checks, weight, support = self.cb_decoder.decode(syndrome)
        # min_weight = self.min_weight
        
        # while not np.all(syndrome.astype(bool) == recovered_checks):
        #     min_weight *= .5
        #     print(f'Min weight reduction to: {min_weight}')
        #     self.cb_decoder.update_weight(min_weight)
        #     if min_weight < 1e-100:
        #         break

        
        if not np.all(syndrome.astype(bool) == recovered_checks):
            # print('Yoink \n')
            #######  TODELETE ##########
            # print(f'Min Weight by default: {self.min_weight}')
            # print(weight)
            # print(f'Number of closed branches: {len(weight)}')
            # print(f'Average Weight = {sum(weight)/len(weight)}')
            # print(f'Maximum weight {max(weight)}')
            # print(f'Min weight {min(weight)}')
            # print(f'SUPPORT')
            # print(support)
            # print(f'Average support = {sum(support)/len(support)}')
            # print(f'Maximum support {max(support)}')
            # print(f'Min weight {min(support)}')
            ###############################
            return np.zeros(self.pcm.shape[1], dtype = int)

        
        ########  TODELETE ##########
        # print(f'Min Weight by deafault: {self.min_weight}')
        # print(weight)
        # print(f'Number of closed branches: {len(weight)}')
        # print(f'Average Weight = {sum(weight)/len(weight)}')
        # print(f'Maximum weight {max(weight)}')
        # print(f'Min weight {min(weight)}')
        # print(f'SUPPORT')
        # print(support)
        # print(f'Average support = {sum(support)/len(support)}')
        # print(f'Maximum support {max(support)}')
        # print(f'Min weight {min(support)}')
        # ################################
        # print('\n')
        # print(f'Average support of the closed branches: {len(weight)}')
        
        
        return recovered_error
        
    # GOTTA USE TRANSFER MATRICES!
    