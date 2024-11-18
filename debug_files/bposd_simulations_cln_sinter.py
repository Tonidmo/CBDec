from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.bp_closed_branch_decoder import BP_CB_decoder
from ldpc import bposd_decoder
import numpy as np
import sinter
from stimbposd import SinterDecoder_BPOSD, sinter_decoders
#### CLN depolarizing channel
import multiprocessing


def generate_example_tasks():    
    l = 12
    m = 6
    if l  == 6:
        rounds = 6
    elif l == 9:
        rounds = 10
    else:
        rounds = 12
    code, A_list, B_list = create_bivariate_bicycle_codes(l, m, [3], [1,2], [1,2], [3])
    # for p in [5e-4, 7.5e-4, 1e-3]:
    for p in [1e-3]:
        yield sinter.Task(
            circuit = build_circuit(code, A_list, B_list, 
                p=p, # physical error rate
                num_repeat=rounds, # usually set to code distance
                z_basis=True,   # whether in the z-basis or x-basis
                use_both=False, # whether use measurement results in both basis to decode one basis
            ),
            json_metadata={
                'l': l,
                'm': m,
                'p': p
            },
        )




if __name__ == "__main__":
    
    samples = sinter.collect(
        num_workers=multiprocessing.cpu_count()-3,
        max_shots=1e10,
        max_errors=100,
        tasks=generate_example_tasks(),
        decoders=['bposd'],
        custom_decoders={"bposd": SinterDecoder_BPOSD(max_bp_iters = 1e3)},
        print_progress=True
    )
    
    for sample in samples:
        # print(f'Distance {d}')
        Pl = sample.errors/sample.shots
        print(f'Logical error = {Pl}')
        # print(Pl/(total_iterations))
        p = sample.json_metadata['p']
        l = sample.json_metadata['l']
        m = sample.json_metadata['m']
        with open(f'data/BBCodes/cln_BPOSD_l{l}_m{m}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl}\n")