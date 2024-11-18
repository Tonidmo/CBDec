from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.closed_branch_decoder import CB_decoder
from src.bp_closed_branch_decoder import BP_CB_decoder
from src.bpbp_closed_branch_decoder import BPBP_CB_decoder
from ldpc import bposd_decoder
from color_code_stim.color_code_stim import ColorCode
import numpy as np
import scipy.io as sio
#### CLN depolarizing channel

if __name__ == "__main__":
    
    d = 11
    
    if d == 5: # l = 6, m = 6
        conts = sio.loadmat('transfermatrices/ColorCodes/CC5transfMat.mat')
    elif d == 7: # l = 6, m = 6
        conts = sio.loadmat('transfermatrices/ColorCodes/CC7transfMat.mat')
    elif d == 9:# l = 9, m = 6
        # conts = sio.loadmat('transfermatrices/transferMatrixcodel9m6.mat')
        conts = sio.loadmat('transfermatrices//ColorCodes/CC9transfMat.mat')
    elif d==11:
        import mat73
        conts = mat73.loadmat('transfermatrices//ColorCodes/CC11transfMat.mat')
    
    max_branches = d**2
    rounds = d
    ps = [1e-4, 2e-4, 3e-4, 4e-4, 5e-4]
    # ps = [5e-4, 7.5e-4, 1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3]
    ps = [4e-4, 7.5e-4]
    NMC = 10**4
    print(f'Color code of distance: d = {d}')
    transf_mat = conts['transfMat']
    H_phen = conts['H_phen']
    obs_phen = conts['obs_phen']
    
    for p in ps:
        print(f'Probability: {p}')
        code = ColorCode(
            d = d,
            rounds = d,
            p_bitflip= p,
            p_reset = p,
            p_meas = p,
            p_cnot = p,
            p_idle = p
        )

        dem = code.circuit.detector_error_model()
        
        bm = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges= True)
        sampler = code.circuit.compile_detector_sampler()
        # Extract pcm and priors
        H = bm.check_matrix.toarray()
        obs = bm.observables_matrix.toarray()
        priors = bm.priors
        
        
        
        # myDecoder = BP_CB_decoder(
        #     H,
        #     priors,
        #     max_num_branches = max_branches,
        #     cts_max = 5,
        #     min_weight = 1e-70,
        # )
        
        myDecoder = BPBP_CB_decoder(
            H,
            obs,
            H_phen,
            obs_phen,
            transf_mat,
            priors,
            min_weight=1e-70,
            max_num_branches=max_branches
        )
        
        # myDecoder = CB_decoder(
        #     H,
        #     priors,
        #     min_weight = 1e-70,
        #     max_num_branches = max_branches
        # )
        
        Pl = 0
        Plogcheck = Pl
        total_iterations = 0
        
        while Pl<150:
            total_iterations += NMC
            detection_events, observable_flips = sampler.sample(NMC, separate_observables = True)
            if Plogcheck != Pl:
                print(f'{Pl}% completed')
                Plogcheck = Pl
            for index, detection_event in enumerate(detection_events):
                observable_flip = observable_flips[index]
                recovered_error = myDecoder.decode(detection_event)
                # recovered_error_obs = (obs @ recovered_error) % 2
                if not np.all(recovered_error == observable_flip):
                    Pl += 1
                    print(f'Errors = {Pl}')
                    print(Pl/(total_iterations*rounds))
                    print('\n')
                    # print(f'Index {index}')
                    # print(f'Current error rate = {100*Pl/(index*(total_iterations/NMC))} \n')
        
        print('Pl BPBPCB')
        print(Pl/(total_iterations*rounds))
        with open(f'data/cln_BPBPCB_color_code_d{d}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl/(total_iterations*rounds)}\n")