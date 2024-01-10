import numpy as np



def bbpcm(
    l : int,
    m : int,
    A_poly : list,
    B_poly : list
):
    S_l = np.roll(np.eye(l), 1, axis = 1)
    S_m = np.roll(np.eye(m), 1, axis = 1)
    
    x = np.kron(S_l, np.eye(m))
    y = np.kron(np.eye(l), S_m)
    
    A = np.zeros((l*m, l*m))
    for element in A_poly:
        if element[0] == 0:
            A = (A + np.linalg.matrix_power(x, element[1])) % 2
        elif element[0] == 1:
            A = (A + np.linalg.matrix_power(y, element[1])) % 2
    B = np.zeros((l*m, l*m))
    for element in B_poly:
        if element[0] == 0:
            B = (B + np.linalg.matrix_power(x, element[1])) % 2
        elif element[0] == 1:
            B = (B + np.linalg.matrix_power(y, element[1])) % 2

    Hx = np.hstack((A, B))
    Hz = np.hstack((B.T, A.T))
    zero_contribution = np.zeros(Hx.shape)
    top = np.hstack((Hx, zero_contribution))
    bottom = np.hstack((zero_contribution, Hz))
    H = np.vstack((top, bottom))
    return H, Hx, Hz
    