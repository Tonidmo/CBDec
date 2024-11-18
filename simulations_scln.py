from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.bpbp_closed_branch_decoder import BPBP_CB_decoder
import numpy as np
import scipy.io as sio
from scipy.io import savemat

#### CLN depolarizing channel

if __name__ == "__main__":
    
    l = 12
    m = 12
    ps = [5*10**-4,10**-3, 3*10**-3, 5*10**-3, 7*10**-3, 10**-2]
    ps = [1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3]
    # Las iteraciones compuestas para estas probabilidades era 900 y 100 en vez de 100 y 1000. 
    ps = [5e-4, 7.5e-4]
    # ps = [2*10**-3]
    # ps = [ 0.005, 10**-2]
    NMC = 10**3
    print('SPARSIFIED VERSION')
    print(f'BB code parameters: l = {l} \t m = {m}')
    if l  == 6:
        rounds = 6
        max_branches = rounds **2
    elif l == 9:
        rounds = 10
        max_branches = rounds **2
    elif l==12 and m==6:
        rounds = 12
        max_branches = rounds **2
    else:
        rounds = 18
        max_branches = rounds **2
        max_branches = int(rounds **2.5)
    
    assert l in [6,9,12]
    
    if l == 6: # l = 6, m = 6
        conts = sio.loadmat('transfermatrices/transferMatrixcodel6m6.mat')
    elif l == 9:# l = 9, m = 6
        # conts = sio.loadmat('transfermatrices/transferMatrixcodel9m6.mat')
        conts = sio.loadmat('transfermatrices/BB108TransfDemsObs.mat')
    elif l==12 and m==6: # l = 12, m = 6
        conts = sio.loadmat('transfermatrices/transferMatrixcodel12m6.mat')
    else: # l = 12, m = 12
        import mat73
        conts = mat73.loadmat('transfermatrices/BB288TransfDemsObs.mat')   
        
        
    code, A_list, B_list = create_bivariate_bicycle_codes(l, m, [3], [1,2], [1,2], [3])
    transf_M = conts['transfMat']
    
    # GENERATING SPARSIFIED CLN PCM

        
    
    for p in ps:
        print(f'Probability p {p}')
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
        obs = bm.observables_matrix.toarray()

        
        priors = bm.priors
        
        columns_to_consider = np.zeros(H.shape[1])

        for column in range(H.shape[1]):
            if sum(H[:,column]) <= 3:
                columns_to_consider[column] = 1
        
        H_phen = H[:,np.where(columns_to_consider==1)[0]]
        obs_phen = obs[:,np.where(columns_to_consider==1)[0]]
        
        min_weight = p**(rounds/2)
        min_weight = 1e-70
        min_weight = p**rounds # For distance 18 only
        
        myDecoder = BPBP_CB_decoder(
            H,
            obs,
            H_phen,
            obs_phen,
            transf_M,
            priors,
            max_num_branches = max_branches,
            max_iter_1 = 1e2,
            max_iter_2 = 1e3,
            cts_max = 5,
            min_weight = min_weight
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
                # recovered_error_obs = (obs @ recovered_error) % 2
                pass
                if not np.all(recovered_error == observable_flip):
                    Pl += 1
                    print(f'Errors = {Pl}')
                    print(f'p \t\t Pl \t\t\t\t Shots \t\t Errors \t\t Index')
                    print(f"{p} \t\t {Pl/(total_iterations*rounds)} \t\t {total_iterations} \t\t {Pl}\t\t\t {index}\n")
                    print('\n')
                    # print(f'Index {index}')
                    # print(f'Current error rate = {100*Pl/(index*(total_iterations/NMC))} \n')
        
        print('Pl BP+CB')
        print(Pl/(total_iterations*rounds))
        with open(f'data/BBCodes/scln_BPCB_l{l}_m{m}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl/(total_iterations*rounds)} \t\t {total_iterations} \t\t {Pl}\n")