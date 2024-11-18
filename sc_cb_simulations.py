from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.closed_branch_decoder import CB_decoder
from ldpc import bposd_decoder
import numpy as np
import stim
#### CLN depolarizing channel

if __name__ == "__main__":
    

    # ps = [5e-4, 7.5e-4, 1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3]
    ps = [1e-3]
    NMC = 10**3
    d = 11
    max_branches = d**2
    print(f'SC code distance: d = {d}')
    print('CB decoding')
        
    
    
    for p in ps[:3]:
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
        bm = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges= True)
        sampler = circuit.compile_detector_sampler()
        # Extract pcm and priors
        H = bm.check_matrix.toarray()
        obs = bm.observables_matrix.toarray()
        priors = bm.priors
        
        min_weight = 1e-70
        
        # myDecoder = BP_CB_decoder(
        #     H,
        #     priors,
        #     max_num_branches = max_branches,
        #     cts_max = 5,
        #     min_weight = min_weight,
        # )
        
        myDecoder = CB_decoder(
            H,
            priors,
            min_weight = 1e-70,
            max_num_branches = max_branches
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
                recovered_error_obs = (obs @ recovered_error) % 2
                if not np.all(recovered_error_obs == observable_flip):
                    Pl += 1
                    print(f'Errors = {Pl}')
                    print(Pl/(total_iterations))
                    print('\n')
                    # print(f'Index {index}')
                    # print(f'Current error rate = {100*Pl/(index*(total_iterations/NMC))} \n')
        
        print(f'Pl CB for probability {p}')
        print(Pl/(total_iterations))
        with open(f'data/cln_CB_sc_{d}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl/(total_iterations)}\n")