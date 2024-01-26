import numpy as np
from pcm_construction.bbcodes import bbpcm
from src.noise.data_qubit import depolarizing_round, destructive_error
from src.closed_branch_decoder import CB_decoder
from scipy.linalg import null_space



if __name__ == "__main__":
    # We will first create the parity check matrix. For this example, it will be l = 6, m = 6 A_poly = 
    l = 6
    m = 6 
    # A polynomial = x^3+y+y^2
    A_poly = [[0,3], [1,1], [1,2]]
    # B polynomial = y^3 + x + x^2
    B_poly = [[1,3], [0,1], [0,2]]

    H, Hx, Hz = bbpcm(l = l, m = m, A_poly= A_poly, B_poly = B_poly)

    Hx_nullspace = null_space(Hx)
    Hz_nullspace = null_space(Hz)
    
    # TODO los errores x no deberían formar parte del nullspace the Hz ni los z del nullspace de Hx

    # ps = np.linspace(0.005, 0.04, num = 8)
    ps = [ 0.02]
    NMC = [10**4]
    Pl = 0        
    n_branches = 10
    n_growths = 6
    name_file = f'data\data_l{l}_m{m}_ng{n_growths}_nb{n_branches}2.txt'
    for index, p in enumerate(ps):
        print(f'Prob: {p}')
        model = (H, p)    
        myDecoder = CB_decoder(model, max_branches = n_branches, max_growths = n_growths, bp_reweighting= False)
        for i in range(NMC[index]):
            print(f'Numero {i}')
            error = destructive_error(H)
            syndrome = (np.dot(H, error) % 2).astype(int)

            error_recovered = myDecoder.decode(syndrome, comments = False)

            tot_err = error_recovered ^ error
            
            if np.all(tot_err == 0):
                continue
            
            elif not np.all((np.dot(H, tot_err) % 2).astype(int) == 0):
                Pl += 1/NMC[index]
                continue
            tot_errorx = tot_err[:H.shape[1]//2]
            if not np.all((np.dot(Hz_nullspace.T, tot_errorx) % 2).astype(int) == 0):
                Pl += 1/NMC[index]
                continue
            
            tot_errorz = tot_err[H.shape[1]//2:]
            if not np.all((np.dot(Hx_nullspace.T, tot_errorz) % 2).astype(int) == 0):
                Pl += 1/NMC[index]
                continue
        with open(name_file, 'a') as file:
            file.write(f'{p}\t\t {Pl}\n')
            print(f'{p}\t\t {Pl}\n')
        