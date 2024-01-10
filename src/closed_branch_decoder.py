import stim
import numpy as np
from beliefmatching import detector_error_model_to_check_matrices
import copy
from typing import Union
from sinter import Decoder
from ldpc.osd import bposd_decoder
from ldpc import bp_decoder
from src.branch import Branch, Closed_Branch, Cluster
from sinter import Decoder


class CB_decoder:

    def __init__(
            self,
            model: Union(stim.DetectorErrorModel, (np.ndarray, float)),
            max_branches: int = 25,
            max_growths: int = 5,
            max_cts: int = 3,
            max_bp_iters: int = 30,
            bp_method: str = "product_sum",
            bp_reweighting: bool = True,
            **bposd_kwargs
    ):
        
        self.max_branches = max_branches
        self.max_growths = max_growths
        self.bp_reweighting  = bp_reweighting
        self.max_cts = max_cts
        
        
        if isinstance(model, stim.DetectorErrorModel):
            self.data = False
            self._matrices = detector_error_model_to_check_matrices(model, allow_undecomposed_hyperedges=True)


            self._bp = bp_decoder(
                parity_check_matrix=self._matrices.check_matrix,
                max_iter=max_bp_iters,
                bp_method=bp_method,
                channel_probs=self._matrices.priors,
                **bposd_kwargs
            )
            self.pcm = self._matrices.check_matrix
            self.llr = np.log(self._matrices.priors/(1-self._matrices.priors))
        
        else:
            self.data = True
            self.pcm = model[0]
            priors = np.full(self.pcm.shape[1], model[1])
            self._bp = bp_decoder(
                parity_check_matrix=self.pcm,
                max_iter=max_bp_iters,
                bp_method=bp_method,
                channel_probs=priors,
                **bposd_kwargs
            )
            self.llr = np.log(priors/(1-priors))
        
        self.m, self.n = self.pcm.shape


    def weight_1_errors(
            self,
            syndrome: np.array ,
            weight : float,
            cluster : Cluster,
            reordered_llr: np.array,
            reordered_binary_matrix: np.ndarray,
            pc : bool = False
    ) -> Cluster:
        
        # Weight 1 events.

     
        # Get the indices where syndrome equals 1
        checks_to_flip = np.bitwise_xor(cluster.checks, syndrome)
        ones_indices = np.where(checks_to_flip == 1)[0]
        # Get the columns where syndrome equals 1
        for col in range(self.n):
            if np.ravel(reordered_llr)[col] > weight:
                continue
            column = reordered_binary_matrix[:, col]


            if np.all(np.isin(column[:, 0].nonzero()[0], ones_indices)):
                checks = np.zeros(self.m)

                checks[column[:, 0].nonzero()[0]] = 1
                events = np.zeros(self.n)
                events[col] = 1
                cb_to_add = Closed_Branch(checks.astype(int), events.astype(int))
                # for cb in cluster.closed_branches_2:
                #     assert cb != cb_to_add
                cluster.include_closed_branch_to_cluster(cb_to_add, pc = pc)
                cluster.add_check_to_cluster(checks)
                cluster.add_event_to_cluster(events)
                # for check in np.where(cluster.checks == 1)[0]:
                #     assert len([1 for branch in cluster.closed_branches_2 if branch.checks[check] == 1]) <= 1 or len([1 for branch in cluster.closed_branches_1 if branch.checks[check] <= 1])
                checks_to_flip = np.bitwise_xor(cluster.checks, syndrome)
                ones_indices = np.where(checks_to_flip == 1)[0]

        return cluster

    def non_dest_branch_growing(
            self, 
            trivial_cts : int, 
            cluster : Cluster, 
            syndrome : np.array, 
            reordered_llr : np.array, 
            weight : float, 
            reordered_binary_matrix : np.ndarray,
            max_branches : int,
            destruction : bool = False
        ) -> Cluster:
        # detectar instancias de ramas (columnas con un número mínimo de un check no trivial) y un número de trivial_cts triviales.
        # Crecerlas hasta que desaparezcan por perdida de peso o se cierren. Devolver en el cluster 2.
        
        checks_to_flip = np.bitwise_xor(cluster.checks, syndrome)
        ones_indices = np.where(checks_to_flip == 1)[0]
        # print(f'Non trivial syndrome elements that we must flip: {len(ones_indices)}')
        # Ones indices are the only ones that we can flip.

        for col in range(self.n):
            
            if np.array_equal(syndrome, cluster.checks):
                break


            if reordered_llr[ col] > weight:
                continue
            else:
                weight_of_branch = weight - reordered_llr[col]
            
            
            column = reordered_binary_matrix[:, col]

            check_nodes = np.intersect1d(column[:, 0].nonzero()[0], ones_indices)
            checks_to_search = np.setdiff1d(column[:, 0].nonzero()[0], ones_indices)
            # TODO Consider destruction case in which touching another closed_tree from the beginning destroys them.

            if len(check_nodes) > 0 and len(checks_to_search) == trivial_cts:

                branches = []
                checks = np.zeros(self.m)
                events = np.zeros(self.n)
                checks[check_nodes] = 1
                events[col] = 1
                cluster_copy = copy.deepcopy(cluster)
                cluster_copy.add_check_to_cluster(checks)
                cluster_copy.add_event_to_cluster(events)

                # We must create the branch:
                if trivial_cts == 1:
                    branch = Branch(
                        pcm = reordered_binary_matrix,
                        checks = checks,
                        events = events,
                        check_to_search = int(checks_to_search[0]),
                        weight_to_consider = weight_of_branch,
                        clusters_to_consider = cluster_copy,
                        sepd = [],
                        sepc = [],
                        ptbf = 1
                    )


                elif trivial_cts > 1:
                    branch = Branch(
                        pcm = reordered_binary_matrix,
                        checks = checks,
                        events = events,
                        check_to_search = int(checks_to_search[0]),
                        weight_to_consider = weight_of_branch,
                        clusters_to_consider = cluster_copy,
                        sepd = [list(checks_to_search)],
                        sepc = [int(checks_to_search[0])],
                        ptbf = 1
                    )
                    # for i in range(len(branch.sepc)):
                    #     assert branch.sepc[i] in branch.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                    # for sep in branch.sepd:
                    #     if len(sep) < 2:
                    #         pass
                
                branches.append(branch)

                # Mirar de cambiar a While True hasta que se encuentre rama cerrada o se termine el peso de las ramas abiertas y retorne lista vacía.
                #for growth in range(1,numb_growths + 1):
                i = 0
                if col == 1951:
                    pass
                while True:
                    i += 1 
                    # if i > 1:
                    #     old_new_branches = copy.deepcopy(new_branches)
                        # TODO: to look why br != branches
                    new_branches = []
                    # changed = False
                    for j in range(len(branches)):
                        branch = copy.deepcopy(branches[j])
                        # for m in range(len(branches[j].sepc)):
                        #     assert branches[j].sepc[m] in branches[j].sepd[m], 'Fallo sepd'
                        # assert len(branches[j].sepd) == len(branches[j].sepc), 'Fallo dimensiones sepd sepc'
                        branch_growth = branch.grow_branch(
                            reordered_llr,
                            syndrome,
                            destruction = destruction
                        )
                        if len(branch_growth) == 1 and branch_growth[0].ptbf == 0:
                            # Branch has been closed
                            new_branches = branch_growth
                            break
                        else:
                            # Branch has returned grown, open branches.
                            new_branches += branch_growth
                            
                    if len(new_branches) == 0:
                        # Ran out of weight, nothing to grow.
                        # print('Ran out of weight')
                        break

                    if len(new_branches) == 1 and new_branches[0].ptbf == 0:
                        # Success
                        break

                    if len(new_branches) > max_branches:
                        break

                    weight_values = [branch.separation_number() for branch in new_branches]
                    threshold = min(weight_values)
                    branches = []
                    for branch in new_branches:
                        if weight_values[new_branches.index(branch)] == threshold:
                            branches.append(branch)

                    # branches = [branch for branch in new_branches if weight_values[new_branches.index(branch)] == threshold]


                    
                    # print('After')
                    # for branch in branches:
                    #     for sep in branch.sepd:
                    #         print(sep)
                    #         if len(sep) < 2:
                    #             pass
                    # print('\n')

                    # br = copy.deepcopy(branches)

                    # for branch in br:
                    #     branch.sepd = [tuple(sep) for sep in branch.sepd]

                    # del branches
                    
                
                if len(new_branches) > 0:
                    if len(new_branches) == 1 and new_branches[0].ptbf == 0:
                        # print('HERE')
                        # FALTA PONER LOS CHECKS Y EVENTS DEL NEW_BRANCH AL CLUSTER
                        new_branch = new_branches[0]
                        cluster = new_branch.cluster
                        closed_branch = Closed_Branch(new_branch.checks, new_branch.events) # Potser sigui aquí
                        cluster.include_closed_branch_to_cluster(closed_branch, destruction)
                        # for check in np.where(cluster.checks == 1)[0]:
                        #     assert len([1 for branch in cluster.closed_branches_2 if branch.checks[check] == 1]) <= 1 or len([1 for branch in cluster.closed_branches_1 if branch.checks[check] <= 1])
                        checks_to_flip = np.bitwise_xor(cluster.checks, syndrome)
                        ones_indices = np.where(checks_to_flip == 1)[0]
                        
        return cluster



    def decode(self, syndrome, comments = False) -> np.array:
        """
        Decode the syndrome and return a prediction of which observables were flipped

        Parameters
        ----------
        syndrome : np.ndarray
            A single shot of syndrome data. This should be a binary array with a length equal to the
            number of detectors in the `stim.Circuit` or `stim.DetectorErrorModel`. E.g. the syndrome might be
            one row of shot data sampled from a `stim.CompiledDetectorSampler`.

        Returns
        -------
        np.ndarray
            A binary numpy array `predictions` which predicts which observables were flipped.
            Its length is equal to the number of observables in the `stim.Circuit` or `stim.DetectorErrorModel`.
            `predictions[i]` is 1 if the decoder predicts observable `i` was flipped and 0 otherwise.
        """

        # Case in which syndrome is all 0:

        n, m = self.pcm.shape

        if np.all(syndrome == np.zeros(m)):
            if not self.data:
                return (self._matrices.observables_matrix @ np.zeros(n)) % 2
            else:
                return np.zeros(n)



        if self.bp_reweighting:
            corr = self._bp.decode(syndrome)
            if self._bp.converge == 1:
                # BP has converged, we return result:
                if not self.data:
                    return  (self._matrices.observables_matrix @ corr) % 2
                else:
                    return corr
            else:
                if not np.any(np.isinf(self._bp.log_prob_ratios)) and not np.any(np.isnan(self._bp.log_prob_ratios)):
                    llr = self._bp.log_prob_ratios
                    llr = llr - min(llr)
                else:
                    llr = self.llr - min(self.llr) + 1
        else:
            llr = self.llr 
        
        if comments:
            print('BP fails')
            print(list(syndrome))
            
        # ORDERING THE PCM SO AS TO CONSIDER DENSER EVENTS FIRST
        # We order following the llrs,  from smaller to larger
        # ones_count_per_column = np.sum(self.pcm, axis=0).astype(int)

        # sorted_indices = np.argsort(ones_count_per_column)[0]
        sorted_indices = np.argsort(llr)# Increasing values because lower ones aremore probable

        reordered_binary_matrix = self.pcm[:, np.ravel(sorted_indices)]
        reordered_llr = llr[sorted_indices]




        for step in range(1, self.max_growths):
            if comments:
                print(f'\nSTEP NUMBER {step}')
                print(f'Weight of syndrome {np.sum(syndrome)}\n')
            # We should change the pcm, so as to make it that we iterate before over denser columns.

            # weight = (sum(llr)/len(llr)) + (step*(max(llr)/2)) # We write 
            weight = (step*(max(llr))) # We write 
            if comments:
                print(f'Weight = {weight}')
            # weight = max(llr)*step

            # We introduce clusters
            
            checks = np.zeros(self.m).astype(int)
            events = np.zeros(self.n).astype(int)
            cluster = Cluster(checks, events, closed_branches_1 = [], closed_branches_2 = [])


            #------------------------------------------------------------------------------------------

            # WEIGHT-1 ERRORS

            if comments:
                print(f'Weight one errors')
            cluster = self.weight_1_errors(syndrome, weight, cluster, reordered_llr, reordered_binary_matrix)
            

            if comments:
                print(f'Weight syndrome')
                print(f' {np.sum(syndrome)- np.sum(cluster.checks)}\n')
                # print(f' Number of events considered: {sum[cluster.closed_branches_2.events]}')
            # return condition if all non_trivial checks have been flipped.
            
            if np.array_equal(syndrome, cluster.checks):
                if not self.data:
                    return (self._matrices.observables_matrix @ cluster.events[np.argsort(np.ravel(sorted_indices))]) % 2
                else:
                    return (cluster.events[np.argsort(np.ravel(sorted_indices))])
            
            #------------------------------------------------------------------------------------------


            # NON DESTRUCTION GROWTH
            for tcts in range(1, self.max_cts + 1):

                if comments:
                    print(f'{tcts} check nodes to search Non-Destructive branch growth:')
                    
                # Hacer función que te mira cuantos checks triviales tienes en una columna, si son "tcts" y tiene como mínimo un check_node, palante.
                cluster = self.non_dest_branch_growing(
                    tcts, 
                    cluster, 
                    syndrome, 
                    reordered_llr, 
                    weight, 
                    reordered_binary_matrix, 
                    self.max_branches
                )
                
                if comments:
                    print(f'Weight syndrome')
                    print(f' {np.sum(syndrome)- np.sum(cluster.checks)}\n')


                # We check if the syndrome condition has been satisfied.
                if np.array_equal(syndrome, cluster.checks):
                    if not self.data:
                        return (self._matrices.observables_matrix @ cluster.events[np.argsort(np.ravel(sorted_indices))]) % 2
                    else:
                        return (cluster.events[np.argsort(np.ravel(sorted_indices))])
            


            #------------------------------------------------------------------------------------------
            
            # DESTRUCTION GROWTH
            # for tcts in range(1, self.max_cts + 1):

            if comments:
                print(f'{tcts} check nodes to search DESTRUCTIVE branch growth:\n')
            # Hacer función que te mira cuantos checks triviales tienes en una columna, si son "tcts" y tiene como mínimo un check_node, palante.
            cluster = self.non_dest_branch_growing(tcts, cluster, syndrome, reordered_llr, weight, reordered_binary_matrix, self.max_branches, destruction = True)

            # We check if the syndrome condition has been satisfied.
            if np.array_equal(syndrome, cluster.checks):
                if not self.data:
                    return (self._matrices.observables_matrix @ cluster.events[np.argsort(np.ravel(sorted_indices))]) % 2
                else:
                    return (cluster.events[np.argsort(np.ravel(sorted_indices))])

            if comments:
                print(f'Weight 1 ND error recovering:')
            cluster = self.weight_1_errors(syndrome, weight, cluster, reordered_llr, reordered_binary_matrix)

            # We check if the syndrome condition has been satisfied.
            if np.array_equal(syndrome, cluster.checks):
                if not self.data:
                    return (self._matrices.observables_matrix @ cluster.events[np.argsort(np.ravel(sorted_indices))]) % 2
                else:
                    return (cluster.events[np.argsort(np.ravel(sorted_indices))])

            if comments:
                print(f'1 cts ND error recovering:')
                print(f' {np.sum(syndrome)- np.sum(cluster.checks)} checks to flip')

            cluster = self.non_dest_branch_growing(
                1, 
                cluster, 
                syndrome, 
                reordered_llr, 
                weight, 
                reordered_binary_matrix, 
                self.max_branches
            )
            
            if comments:
                print(f'Weight syndrome after {tcts} DESTRUCTIVE growth')
                print(f' {np.sum(syndrome)- np.sum(cluster.checks)} checks to flip')
            # We check if the syndrome condition has been satisfied.
            if np.array_equal(syndrome, cluster.checks):
                if not self.data:
                    return (self._matrices.observables_matrix @ cluster.events[np.argsort(np.ravel(sorted_indices))]) % 2
                else:
                    return (cluster.events[np.argsort(np.ravel(sorted_indices))])



        # We check if the syndrome condition has been satisfied.
        if np.array_equal(syndrome, cluster.checks):
            return (self._matrices.observables_matrix @ cluster.events[np.argsort(np.ravel(sorted_indices))]) % 2
        else:
            return (self._matrices.observables_matrix @ np.zeros(self.n)) % 2


    def decode_batch(self, shots: np.ndarray) -> np.ndarray:
        # This function only available under CLN using stim
        predictions = np.zeros((shots.shape[0], self._matrices.observables_matrix.shape[0]), dtype=bool)
        for i in range(shots.shape[0]):
            predictions[i, :] = self.decode(shots[i, :])
        return predictions