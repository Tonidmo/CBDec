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
    ps = np.linspace(0.0006, 0.0008, num = 3)
    NMC = 10**6
    pcm = np.ndarray([3, 2, 1])
    max_branches = 10
    max_growths = 5
    for p in ps:
        Pl = 0
               
        
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