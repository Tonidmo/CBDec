from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.closed_branch_decoder import CB_decoder
import pymatching
import numpy as np
import stim
#### CLN depolarizing channel

if __name__ == "__main__":
    

    ps = [5e-4, 7.5e-4, 1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3]
    NMC = 10**4
    d = 11
    print(f'SC code distance: d = {d}')
    print('MATCHING')
        
    
    
    for p in ps[3:]:
        print(f'Probability: {p}')
        circuit = stim.Circuit.generated(
            "surface_code:rotated_memory_z",
            rounds=d,
            distance=d,
            after_clifford_depolarization=p,
            after_reset_flip_probability=p,
            before_measure_flip_probability=p,
            before_round_data_depolarization=p)
        
        dem = circuit.detector_error_model()
        sampler = circuit.compile_detector_sampler()
        matcher = pymatching.Matching.from_detector_error_model(dem)

        
        Pl = 0
        Plogcheck = Pl
        total_iterations = 0
        
        
        while Pl<100:
            total_iterations += NMC
            detection_events, observable_flips = sampler.sample(NMC, separate_observables = True)
            predictions = matcher.decode_batch(detection_events)
            if Plogcheck != Pl:
                print(f'{Pl}% completed')
                Plogcheck = Pl
            for index, detection_event in enumerate(detection_events):
                observable_flip = observable_flips[index]
                if not np.all(predictions[index] == observable_flip):
                    Pl += 1
                    print(f'Errors = {Pl}')
                    print(Pl/(total_iterations))
                    print('\n')
                    # print(f'Index {index}')
                    # print(f'Current error rate = {100*Pl/(index*(total_iterations/NMC))} \n')
        
        print('Pl CB')
        print(Pl/(total_iterations))
        with open(f'data/cln_MX_sc_{d}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl/(total_iterations)}\n")