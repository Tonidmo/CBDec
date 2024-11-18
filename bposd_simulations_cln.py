from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.bp_closed_branch_decoder import BP_CB_decoder
from ldpc import bposd_decoder
import numpy as np
#### CLN depolarizing channel

if __name__ == "__main__":
    
    l = 12
    m = 12
    ps = [.0015, .001]
    NMC = 10**3
    print(f'BB code parameters: l = {l} \t m = {m}')
    if l  == 6:
        rounds = 6
        max_branches = 36
        code, A_list, B_list = create_bivariate_bicycle_codes(l, m, [3], [1,2], [1,2], [3])
    elif l == 9:
        rounds = 10
        max_branches = 100
        code, A_list, B_list = create_bivariate_bicycle_codes(l, m, [3], [1,2], [1,2], [3])
    elif l == 12 and m == 6:
        rounds = 12
        max_branches = 144
        code, A_list, B_list = create_bivariate_bicycle_codes(l, m, [3], [1,2], [1,2], [3])
    elif l == 12 and m == 12:
        rounds = 18
        max_branches = rounds**2
        code, A_list, B_list = create_bivariate_bicycle_codes(l, m, [3], [2,7], [1,2], [3])
        
        
    
    for p in ps:
        print(f'Probability: {p}')
        circuit = build_circuit(code, A_list, B_list, 
                        p=p, # physical error rate
                        num_repeat=rounds, # usually set to code distance
                        z_basis=True,   # whether in the z-basis or x-basis
                        use_both=False, # whether use measurement results in both basis to decode one basis
                        )
        
        dem = circuit.detector_error_model()
        bm = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges= True)
        sampler = circuit.compile_detector_sampler()
        # Extract pcm and priors
        H = bm.check_matrix.toarray()
        print(f'Numero de filas: {H.shape}')
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
        with open(f'data/BBCodes/cln_BPOSD_l{l}_m{m}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl/(total_iterations*rounds)} \t\t {total_iterations} \t\t {Pl}\n")