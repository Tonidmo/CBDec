import stim
# from quasicyclic import quasi_cyclic_from_params, QuasiCyclic
# from quasicyclic.bp_osd import BPOSD
import numpy as np
from beliefmatching import detector_error_model_to_check_matrices
from src.closed_branch_decoder import CB_decoder

def simulation(myDecoder, detection_events, observable_flips):
    result = myDecoder.decode(detection_events.astype(int), comments = True)
    if not np.array_equal(observable_flips.astype(int), result.astype(np.uint8)):
        return True, result
        # print('Nay')
        # print(detection_events[0].astype(int))
        # Pl += 1/NMC
    else:
        return False, result


if __name__ == '__main__':
    # l = 6
    # m = 6
    # A_poly = "x^3 + y + y^2"
    # B_poly = "y^3 + x + x^2"
    # qc: QuasiCyclic = quasi_cyclic_from_params(l=l, m=m, A_poly= A_poly, B_poly=B_poly)
    ps = np.linspace(0.0006, 0.0008, num = 3)
    NMC = 10**6
    pcm = np.ndarray([3, 2, 1])
    # with open(name_file, 'a') as file:
        # file.write(f"p \t \t Pl\n")
    # if  l == 6:
    #     rounds = 6
    # elif l == 9:
    #     rounds = 10
    # elif l == 12:
    #     rounds = 12
    # max_branches = rounds ** 2
    # name_file = f"l{l}_m{m}_n_branches{max_branches}.txt"
    for p in ps:
        Pl = 0
        
        # circuit: stim.Circuit = qc.generate_circuit(measure_basis="X", num_rounds=rounds, p=p, only_include_same_basis_detectors = True)
        # dem = circuit.detector_error_model()
        
        # sampler = circuit.compile_detector_sampler()
        
        
        pcm = detector_error_model_to_check_matrices(dem, allow_undecomposed_hyperedges=True)
        myDecoder =  CB_decoder(model = dem, bp_reweighting = True, max_branches = max_branches, max_growths = rounds)
        
        detection_events, observable_flips = sampler.sample(NMC, separate_observables=True)
        percentage = 0.01
        for i in range(NMC):
            
            # print(f' Numero: {i}')
            if i/NMC > percentage:
                print(f'{int(percentage * 100)}% completed')
                percentage += 0.01


            boole, result = simulation(myDecoder, detection_events[i], observable_flips[i])
            if boole:
                Pl += 1/NMC
                print(Pl)
                # print('Nay')
                print(list(detection_events[i]))
                print(list(observable_flips[i]))
                print(list(result))

            # print('\n')
            # a = simulation(myDecoder, sampler)
            # print(a)



        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     results = [executor.submit(simulation, myDecoder, sampler) for _ in range(NMC)]
        
        #     for f in concurrent.futures.as_completed(results):
        #         print(f.result())
        #         if f.result:
        #             Pl += 1/NMC





        with open(name_file, 'a') as file:
            file.write(f"{p} \t \t {Pl}\n")
        print(f'p = {p} \t  Pl = {Pl}')