# The Closed Branch Decoder under data qubit noise. - Guided example

This document provides an example on how to use the Closed Branch decoder for [bivariate bicycle (BB) codes](https://arxiv.org/abs/2308.07915) under data qubit noise. In order to simulate the same noise model on another code, the process would be the same but providing another parity check matrix.

## Decoding a single pure data qubit noise round

We begin by installing the dependencies needed for our code and creating a desired BB code. We will use `numpy` for manipulating arrays and `bbpcm` for code generation. The bbpcm function is provided and allows us to construct a [BB codes](https://arxiv.org/abs/2308.07915) returing its parity check matrix `H` and its constituent `Hx` and `Hz` based on the incoming parameters `l`, `m` and the polynomials `A_poly` and `B_poly`. Where rows of the Hx and Hz matrices correspond to checks susceptible to $X$ and $Z$ operators on the data qubits correspondingly.

```python
import numpy as np
from pcm_construction.bbcodes import bbpcm

# We will first create the parity check matrix. For this example, it will be l = 6, m = 6 A_poly = 
l = 6
m = 6 
# A polynomial = x^3+y+y^2
A_poly = [[0,3], [1,1], [1,2]]
# B polynomial = y^3 + x + x^2
B_poly = [[1,3], [0,1], [0,2]]

H, Hx, Hz = bbpcm(l = l, m = m, A_poly= A_poly, B_poly = B_poly)

```

Now, given the parity check matrix and a probability error `p` for every qubit within the code, using `depolarizing_round`, we can simulate an error `e` on the code. The syndrome `z` that error produces on the code is obtained through the product of the parity check matrix of the code `H` with the error `e`. 

```python
from src.noise.data_qubit import depolarizing_round

# Probability error
p = 0.03 #3%

# Depolarizing error round.
e = depolarizing_round(p, H.shape[1])

# Syndrome produced
z = np.dot(H, e) % 2

```

We now move to define the `CB_decoder` class in order to decode the syndrome. The first parameter necessary for defining the `CB_decoder` is a `model`, which can either be `stim.DetectorErrorModel` object or a duple containing `H` and `p`, for our data qubit channel consideration, we will use the duple. As explained on the article, the decoder is defined by the number of branches it allows when growing branch instances (`n_branches`), the number of growths it considers (`n_growths`), the maximum number of trivial checks it considers for branch instances (`max_cts`) and if it considers BP in order to enhance its performance (`bp_reweighting`). There are additional parameters related to the BP decoder which can be seen in `src/closed_branch_decoder.py`.

```python

from src.closed_branch_decoder import CB_decoder

model = (H, p) 
n_branches = 10
n_growths = 5
max_cts = 3
bp_reweighting = True



myDecoder = CB_decoder(model, max_branches = n_branches, max_growths = n_growths, max_cts = 3, bp_reweighting = True)

```

Once the decoder is defined, we can use it to decode the previously defined syndrome `z` and see if our recovered error `rec_e` result is correct. In order to do that, we will follow the process from [P. Fuentes et al](https://ieeexplore.ieee.org/abstract/document/9850409) and use the nullspace of the aforementioned `Hx` and `Hz`.


```python

# The comments argument provides a description of the CB_decoder in the case where BP failes to converge.
rec_e = = myDecoder.decode(syndrome, comments = True)

# We combine the recovered error with the original one:
tot_err = rec_e ^ error

from scipy.linalg import null_space

Hx_nullspace = null_space(Hx)
Hz_nullspace = null_space(Hz)

```

We can now jump to the results by considering the conditions which need to be satisfied for the recovered error `tot_err` to act trivially on the codespace and thus having corrected the syndrome successfully.

```python

# If tot_err is a trivial error, the syndrome has been successfully decoded.
if np.all(tot_err == 0):
    print('Success')

# If the recovered error does not adjust to the syndrome, the decoding process has failed.
elif not np.all((np.dot(H, tot_err) % 2).astype(int) == 0):
    print('Failure')

# We proceed to divide the tot_err considering the $X$ and $Z$ contributions independently. 
tot_errorx = tot_err[:H.shape[1]//2]
tot_errorz = tot_err[H.shape[1]//2:]

# If the product of the nullspace of Hz with the $X$ contribution of the error is not trivial, we have acted non-trivially on the codespace, and thus, the decoding process has failed. Same applies to the $Z$ contribution of the error and the nullspace of Hx.
if not np.all((np.dot(Hz_nullspace.T, tot_errorx) % 2).astype(int) == 0):
    print('Failure')


if not np.all((np.dot(Hx_nullspace.T, tot_errorz) % 2).astype(int) == 0):
    print('Failure')

```

## Computing a logical error curve and plotting it

