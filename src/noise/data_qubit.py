import numpy as np


def depolarizing_round(p : float, n : int) -> np.array:
    """
    Introduce a probability of error and a parity check matrix and returns a 2n symplectic error vector.

    Args:
        p (float): probability of error
        n (int): number of columns
    """
    assert n % 2 == 0, "The value of columns of a quantum parity check matrix should be even."
    values = [0, 1, 2, 3] # I, X, Y, Z
    probabilities = [(1-p), p/3, p/3, p/3]
    
    random_array = np.random.choice(values, size = n//2, p = probabilities)
    error = np.zeros(n, dtype = int)
    
    for i in range(n//2):
        if random_array[i] == 0:
            continue
        elif random_array[i] == 1:
            error[i] = 1
        elif random_array[i] == 2:
            error[i] = 1
            error[i + n//2] = 1
        elif random_array[i] == 3:
            error[i + n//2] = 1
    
    return error