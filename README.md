# CBDec
 
 The closed branch decoder is a new type of generic decoder for quantum error correcting codes. In this repository we provide our code as a tool for interested readers so they can make simulations on other quantum error correcting codes provided that they have a parity check matrix. This is the first version of the code, which has been done entirely in Python, thus, the speed needs to be improved to a great amount. Neverthless, it provides an interesting sand box for researchers interested on the decoder.

 ## Utilization of the repository

This repository can be employed in order to make simulations of the closed branch decoder on arbitrary quantum error correcting codes. For simulations, this repository will provide a template for data qubit noise, phenomenological noise and circuit-level noise. In all this instances, we consider depolarizing noise.

## Installation

Once the repository has been cloned, in order to start using the CBDec repository, you should start by installing all the necessary python packages through:

```bash

pip install -r requirements.txt

```



## Examples

In order to initiate yourselves on the way this repository works, there are three .md files with examples showing the way in which this repositary can be used. This are:

1. `examples/data_noise_example.md` for data qubit noise.
2. `examples/phenomenological_noise_example` for phenomenological noise.
3. `examples/circuit_level_noise_example` for circuit-level noise.

## Dependencies

Beliefmatching, stim, ldpc (from Jocshka)

## Citation

Please, cite the following article upon publishing results utilizing this repository.

Additionaly, this repository uses modules which should be cited themselves:

1. [Gidney, C., ``Stim: a fast stabilizer circuit simulator.`` *Quantum*  **5**, 497 (2021).](https://github.com/quantumlib/Stim/tree/main)
2. [Roffe, J., ``LDPC: Python tools for low density parity check codes`` (2022)](https://github.com/quantumgizmos/ldpc/tree/main)
3. [Higgott, O., Bohdanowicz, T. C., Kubica, A., Flammia, S. T. and Campbell, E. T. ``Improved Decoding of Circuit Noise and Fragile Boundaries of Tailored Surface Codes.`` *Phys. Rev. X* **13**, 031007 (2023)](https://github.com/oscarhiggott/BeliefMatching)
