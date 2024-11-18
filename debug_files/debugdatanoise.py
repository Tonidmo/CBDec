import numpy as np
from pcm_construction.bbcodes import bbpcm
from src.noise.data_qubit import depolarizing_round, destructive_error
# from bp_closed_branch_decoder import CB_decoder
from src.bp_closed_branch_decoder import BP_CB_decoder
from scipy.linalg import null_space
from bposd import bposd_decoder
import galois    



if __name__ == "__main__":
    # We will first create the parity check matrix. For this example, it will be l = 6, m = 6 A_poly = 
    l = 12
    m = 6 
    
    if l == 6:
        max_branches = 36
    elif l == 9:
        max_branches = 100
    else:
        max_branches = 144
    # A polynomial = x^3+y+y^2
    A_poly = [[0,3], [1,1], [1,2]]
    # B polynomial = y^3 + x + x^2
    B_poly = [[1,3], [0,1], [0,2]]

    H, Hx, Hz = bbpcm(l = l, m = m, A_poly= A_poly, B_poly = B_poly)

    GF = galois.GF(2)

    gf_Hx = galois.GF2(Hx.astype(int))
    gf_Hz = galois.GF2(Hz.astype(int))

    Hx_nullspace = gf_Hx.null_space().view(np.ndarray)
    Hz_nullspace = gf_Hz.null_space().view(np.ndarray)



    #  los errores x no deberían formar parte del nullspace the Hz ni los z del nullspace de Hx

    ps = [ .01, .015, .02, .025, .03, .04, .05, .06, .07, .08][::-1]
    NMC = 1_000_0
    # name_file = f'data/data_l{l}_m{m}.txt'
    name_file = f'data/bposd_data_l{l}_m{m}.txt'

    # For data noise I have considered the following parameters:
    
    # min_weight = 1e-25
    # max_num_branches = 25
    # cts_max = 3


    for index, p in enumerate(ps):
        print(f'Prob: {p}')
        model = (H, p)    
        # myDecoder = BP_CB_decoder(
        #     H,
        #     np.full(H.shape[1], p),
        #     max_num_branches= max_branches
        # )
        myDecoder =  bposd_decoder(
            H,
            error_rate = p,
            channel_probs = [None],
            max_iter = H.shape[1],
            bp_method = "ms",
            ms_scaling_factor = 0.,
            osd_method = "osd_cs",
            osd_order = 0
        )
        
        myDecoder_x = bposd_decoder(
            Hx,
            error_rate = p,
            channel_probs = [None],
            max_iter = 1000,
            bp_method = "ms",
            ms_scaling_factor = 0.,
            osd_method = "osd_cs",
            osd_order = 0
        )
        
        
        myDecoder_z = bposd_decoder(
            Hz,
            error_rate = p,
            channel_probs = [None],
            max_iter = 1000,
            bp_method = "ms",
            ms_scaling_factor = 0.,
            osd_method = "osd_cs",
            osd_order = 0
        )
        
        errors = 0
        iteration_times = 0
        while True:
            iteration_times += 1
            for i in range(NMC):
                print(f'Number {i}')
                error = depolarizing_round(p, H.shape[1])

                
                syndrome = (np.dot(H, error) % 2).astype(int)


                sx = syndrome[:len(syndrome)//2]
                sz = syndrome[len(syndrome)//2:]

                errorx = myDecoder_x.decode(sx)
                errorz = myDecoder_x.decode(sz)
                
                error_recovered = np.concatenate((errorx, errorz))
                
                # error_recovered = myDecoder.decode(syndrome)

                tot_err = error_recovered ^ error
                

                if np.all(tot_err == 0):
                    continue
                elif not np.all((np.dot(H, tot_err) % 2).astype(int) == 0):
                    errors += 1
                    print('1')
                    print(f'Errors: {errors}')
                    print(f'Weight error {np.sum(error)}')
                    print(f'Weight recovered error {np.sum(error_recovered)} \n')
                    continue
                tot_errorx = tot_err[:H.shape[1]//2]
                if not np.all((np.dot(Hz_nullspace, tot_errorx) % 2).astype(int) == 0):
                    errors += 1
                    print('2')
                    print(f'Errors: {errors}')
                    print(f'Weight error {np.sum(error)}')
                    print(f'Weight recovered error {np.sum(error_recovered)} \n')
                    continue
                tot_errorz = tot_err[H.shape[1]//2:]
                if not np.all((np.dot(Hx_nullspace, tot_errorz) % 2).astype(int) == 0):
                    errors += 1
                    print('3')
                    print(f'Errors: {errors}')
                    print(f'Weight error {np.sum(error)}')
                    print(f'Weight recovered error {np.sum(error_recovered)} \n')
                    continue
            if errors > 300:
                print(f'Errors considered: {errors}')
                break
        Pl = errors/ (NMC*iteration_times)
        with open(name_file, 'a') as file:
            file.write(f'{p}\t\t {Pl}\n')
        print(f'{p}\t\t {Pl}\n')
        