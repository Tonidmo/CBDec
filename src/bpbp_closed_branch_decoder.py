# Imports
import numpy as np
from ldpc import bp_decoder
from src.closed_branch_decoder import CB_decoder

# We begin for a model for data qubit noise. Later, we will expand it to a detector error model type of decoder.
class BPBP_CB_decoder():
    
    def __init__(
        self,
        pcm_cln: np.array,
        obs : np.array,
        pcm_scln: np.array,
        obs_phen: np.array,
        transfer_matrix : np.array,
        channel_probs: np.array,
        max_bp_iters: int = 1000,
        max_iter_1: int = 100,
        max_iter_2: int = 1000,
        bp_method: str = "product_sum",        
        min_weight: float = 1e-60,
        max_num_branches: int = 1000,
        cts_max: int = 5
        ) -> None:
        
        self.pcm_cln = pcm_cln
        self.pcm_scln = pcm_scln
        self.obs = obs
        self.obs_phen = obs_phen
        self.transf_M = transfer_matrix
        self.priors = channel_probs
        self.max_branches = max_num_branches
        self.max_bp_iters = max_bp_iters
        self.bp_method = bp_method
        self.min_weight = min_weight
        
        # Maybe change the error rate for channel probabilities

        self.bp_decoder_1 = bp_decoder(
            self.pcm_cln,
            channel_probs = self.priors,
            max_iter = max_iter_1,
            bp_method = self.bp_method
        )
        
        max_numb_cols = 0
        for row in range(self.transf_M.shape[0]):
            num_cols = len(np.where(self.transf_M[row,:]==1)[0])
            if num_cols  > max_numb_cols:
                max_numb_cols = num_cols
        
        
        self.transf_M_red = np.full((self.transf_M.shape[0], max_numb_cols), -1)
        
        for row in range(self.transf_M.shape[0]):
            num_cols = np.where(self.transf_M[row,:]==1)[0]
            self.transf_M_red[row, :len(num_cols)] = num_cols
        
        
        self.priors_phen = self.propagation(self.priors)
        self.bp_decoder_2 = bp_decoder(
            self.pcm_scln,
            channel_probs = self.priors_phen,
            max_iter = max_iter_2,
            bp_method = self.bp_method
        )
        
        self.cb_decoder = CB_decoder(
            self.pcm_scln,
            self.priors_phen,
            min_weight = min_weight,
            max_num_branches = max_num_branches,
            cts_max = cts_max
        ) 
        
        self.m, self.n = self.pcm_cln.shape
        
    def propagation(self, priors):
        p_ph = np.zeros(self.transf_M_red.shape[0])
        for row in range(len(p_ph)):
            columns = self.transf_M_red[row,:]
            try:
                end_index = np.where(columns[:] == -1)[0][0]
            except Exception:
                # if -1 is not found
                end_index = len(columns)
            # primer componente de error
            columns = columns[:end_index]
            pphen_prod = 1
            for i, col in enumerate(columns):
                # Exclude the current element from the product calculation
                pphen_prod *= (1-(2*priors[col]))
            p_ph[row] = .5*(1-pphen_prod)
        return p_ph
        
    def decode(self, syndrome):
        
        # Attempt BP
        recovered_error = self.bp_decoder_1.decode(syndrome)
        
        if self.bp_decoder_1.converge:
            return (self.obs @ recovered_error) % 2
        # If not, compute the weights and begin cb.
        llrs = self.bp_decoder_1.log_prob_ratios
        
        ps = 1/(1+np.exp(llrs))
        eps = 1e-14
        
        ps[ps > 1-eps] = 1-eps
        ps[ps < eps] = eps
        
        
        ps_e = self.propagation(ps)
        
        self.bp_decoder_2.update_channel_probs(ps_e)
        
        recovered_error = self.bp_decoder_2.decode(syndrome)
        
        if self.bp_decoder_2.converge:
            return (self.obs_phen @ recovered_error) % 2
        
        llrs = self.bp_decoder_2.log_prob_ratios
        
        ps = 1/(1+np.exp(llrs))
        eps = 1e-14
        
        ps[ps > 1-eps] = 1-eps
        ps[ps < eps] = eps
        
        self.cb_decoder.update_probabilities(ps)
        # print('CB called')
        
        
        recovered_error, recovered_checks, weight, support = self.cb_decoder.decode(syndrome)
        
        if not np.all(syndrome.astype(bool) == recovered_checks):
            # print('Yoink \n')
            ########  TODELETE ##########
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
            ################################
            return np.zeros(self.pcm.shape[1], dtype = int)
        # print('\n')
        
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
        ################################
        # print('\n')
        return (self.obs_phen @ recovered_error) % 2

    def decode_batch(
        self,
        shots: np.ndarray,
        *,
        bit_packed_shots: bool = False,
        bit_packed_predictions: bool = False,
    ) -> np.ndarray:
        """
        Decode a batch of shots of syndrome data. This is just a helper method, equivalent to iterating over each
        shot and calling `BPOSD.decode` on it.

        Parameters
        ----------
        shots : np.ndarray
            A binary numpy array of dtype `np.uint8` or `bool` with shape `(num_shots, num_detectors)`, where
            here `num_shots` is the number of shots and `num_detectors` is the number of detectors in the `stim.Circuit` or `stim.DetectorErrorModel`.

        Returns
        -------
        np.ndarray
            A 2D numpy array `predictions` of dtype bool, where `predictions[i, :]` is the output of
            `self.decode(shots[i, :])`.
        """
        if bit_packed_shots:
            shots = np.unpackbits(shots, axis=1, bitorder="little")[
                :, : self.num_detectors
            ]
        predictions = np.zeros(
            (shots.shape[0], self.obs.shape[0]), dtype=bool
        )
        for i in range(shots.shape[0]):
            predictions[i, :] = self.decode(shots[i, :])
        if bit_packed_predictions:
            predictions = np.packbits(predictions, axis=1, bitorder="little")
        return predictions
