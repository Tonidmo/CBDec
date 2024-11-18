from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.bp_closed_branch_decoder import BP_CB_decoder
from ldpc import bposd_decoder
import numpy as np
from color_code_stim.color_code_stim import ColorCode
#### CLN depolarizing channel

if __name__ == "__main__":
    
    d = 11
    max_branches = d**2
    rounds = d
    ps = [5e-4, 7.5e-4, 1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3][::-1]
    ps = [5e-4, 7.5e-4, 1e-3, 1.5e-3, 2e-3][::-1]
    ps = [ 5e-4][::-1]
    NMC = 10**3
    print(f'Color code of distance: d = {d}')

        
    
    
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
        #     min_weight = min_weight,
        # )
        
        myDecoder = bposd_decoder(
            H,
            channel_probs = priors,
            osd_order = 0,
            max_iter = 1000
        )
        
        Pl = 0
        Plogcheck = Pl
        total_iterations = 0
        
        while Pl<100:
            total_iterations += NMC
            detection_events, observable_flips = sampler.sample(NMC, separate_observables = True)
            if Plogcheck != Pl:
                print(f'{Pl}% completed')
                Plogcheck = Pl
            for index, detection_event in enumerate(detection_events):
                observable_flip = observable_flips[index]
                recovered_error = myDecoder.decode(detection_event)
                recovered_error_obs = (obs @ recovered_error) % 2
                if not np.all(recovered_error_obs == observable_flip):
                    Pl += 1
                    print(f'Errors = {Pl}')
                    print(Pl/(total_iterations*rounds))
                    print('\n')
                    # print(f'Index {index}')
                    # print(f'Current error rate = {100*Pl/(index*(total_iterations/NMC))} \n')
        
        print('Pl BP+OSD')
        print(Pl/(total_iterations*rounds))
        with open(f'data/cln_BPOSD_color_code_d{d}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl/(total_iterations*rounds)}\n")