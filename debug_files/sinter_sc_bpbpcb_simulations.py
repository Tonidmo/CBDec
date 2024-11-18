from SlidingWindowDecoder.src.build_circuit import build_circuit
from SlidingWindowDecoder.src.codes_q import create_bivariate_bicycle_codes, create_circulant_matrix
from beliefmatching import detector_error_model_to_check_matrices
from src.bpbp_closed_branch_decoder import BPBP_CB_decoder
from ldpc import bposd_decoder
import multiprocessing
import numpy as np
import stim
import sinter
from src.sintercb_decoder import sinterBPBPCBDecoder, sinter_decoders
#### CLN depolarizing channel


def generate_example_tasks():
    for p in [5e-4, 7.5e-4, 1e-3, 1.5e-3, 2e-3, 3e-3, 5e-3, 7e-3]:
    # for p in [5e-4, 7.5e-4, 1e-3, 5e-3, 7e-3]:
    # for p in [5e-4]:
        for d in [5]:
            yield sinter.Task(
                circuit=stim.Circuit.generated(
                    rounds=d,
                    distance=d,
                    after_clifford_depolarization=p,
                    after_reset_flip_probability=p,
                    before_measure_flip_probability=p,
                    before_round_data_depolarization=p,
                    code_task=f'surface_code:rotated_memory_z',
                ),
                json_metadata={
                    'p': p,
                    'd': d,
                },
            )


if __name__ == "__main__":
    

    # ps = [5e-4, 7.5e-4, 1e-3, 5e-3, 7e-3]
    d = 5
    print(f'SC code distance: d = {d}')
    
        
    
    
    # Collect the samples for stimbposd
    samples = sinter.collect(
        # num_workers=8,
        num_workers= 7,
        max_shots= 1e8,
        max_errors=100,
        tasks=generate_example_tasks(),
        decoders=['bpbpcb'],
        custom_decoders=sinter_decoders(),
        print_progress=True
    )

    for sample in samples:
        # print(f'Distance {d}')
        Pl = sample.errors/sample.shots
        print(f'Logical error = {Pl}')
        # print(Pl/(total_iterations))
        p = sample.json_metadata['p']
        with open(f'data/cln_BPBPCB_sc_{d}.txt', 'a') as file:
            file.write(f"{p} \t\t {Pl}\n")