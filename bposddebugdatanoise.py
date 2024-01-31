import numpy as np
from pcm_construction.bbcodes import bbpcm
from src.noise.data_qubit import depolarizing_round
from src.closed_branch_decoder import CB_decoder
from scipy.linalg import null_space
from bposd import bposd_decoder
import galois


if __name__ == "__main__":
    # We will first create the parity check matrix. For this example, it will be l = 6, m = 6 A_poly = 
    l = 6
    m = 6 
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
    
    # TODO los errores x no deberían formar parte del nullspace the Hz ni los z del nullspace de Hx

    # ps = np.linspace(0.005, 0.04, num = 8)
    ps = [0.01, 0.015, 0.02, 0.025, 0.03, 0.04]
    NMC = [10**7, 10**7, 10**6, 10**6, 10**5, 10**5]
    name_file = f'data_l{l}_m{m}_bposd.txt'
    for index, p in enumerate(ps):
        print(f'Prob: {p}')
        Pl = 0        
        
        myDecoder =  bposd_decoder(
            H,
            error_rate = p,
            channel_probs = [None],
            max_iter = H.shape[1],
            bp_method = "ms",
            ms_scaling_factor = 0,
            osd_method = "osd_cs",
            osd_order = 0
        )
        
        for i in range(NMC[index]):
            # print(f'Numero {i}')
            error = depolarizing_round(p, H.shape[1])

            syndrome = (np.dot(H, error) % 2).astype(int)

            myDecoder.decode(syndrome)

            tot_err = myDecoder.osdw_decoding ^ error
            
            if np.all(tot_err == 0):
                continue
            
            elif not np.all((np.dot(H, tot_err) % 2).astype(int) == 0):
                Pl += 1/NMC[index]
                continue
            tot_errorx = tot_err[:H.shape[1]//2]
            if not np.all((np.dot(Hz_nullspace, tot_errorx) % 2).astype(int) == 0):
                Pl += 1/NMC[index]
                continue
            
            tot_errorz = tot_err[H.shape[1]//2:]
            if not np.all((np.dot(Hx_nullspace, tot_errorz) % 2).astype(int) == 0):
                Pl += 1/NMC[index]
                continue
        with open(name_file, 'a') as file:
            file.write(f'{p}\t\t {Pl}\n')
            print(f'{p}\t\t {Pl}\n')
        