from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.bpbp_closed_branch_decoder import BPBP_CB_decoder
from ldpc import bposd_decoder
import numpy as np
import stim
#### CLN depolarizing channel

if __name__ == "__main__":
    

    ps = [5e-4, 7.5e-4, 1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3]
    ps = [3e-3, 5e-3, 7e-3]
    ps = [7.5e-4]
    NMC = 10**3
    d = 9
    max_branches = d**2
    print(f'SC code distance: d = {d}')
    
        
    
    
    for p in ps:
        print(f'Probability: {p}')
        circuit = stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=d,
            distance=d,
            after_clifford_depolarization=p,
            after_reset_flip_probability=p,
            before_measure_flip_probability=p,
            before_round_data_depolarization=p)
        
        dem = circuit.detector_error_model(decompose_errors=True)
        bm = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges= False)
        sampler = circuit.compile_detector_sampler()
        # Extract pcm and priors
        H = bm.check_matrix.toarray()
        obs = bm.observables_matrix.toarray()
        pcm_scln = bm.edge_check_matrix.toarray()
        obs_phen = bm.edge_observables_matrix.toarray()
        priors = bm.priors
        transf_M = bm.hyperedge_to_edge_matrix.toarray()
        
        min_weight = 1e-70
        
        myDecoder = BPBP_CB_decoder(
            H,
            obs,
            pcm_scln,
            obs_phen,
            transf_M,
            priors,
            max_num_branches = max_branches,
            cts_max = 5,
            min_weight = min_weight,
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
                recovered_error = myDecoder.decode(detection_event)[0]
                # recovered_error_obs = (obs_phen @ recovered_error) % 2
                if not np.all(recovered_error == observable_flip):
                    Pl += 1
                    print(f'Errors = {Pl}')
                    print(Pl/(total_iterations))
                    print('\n')
                    # print(f'Index {index}')
                    # print(f'Current error rate = {100*Pl/(index*(total_iterations/NMC))} \n')
        
        print('Pl BPBPCB')
        print(Pl/(total_iterations))
        with open(f'data/surface_codes/cln_BPBPCB_sc_{d}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl/(total_iterations)}\n")