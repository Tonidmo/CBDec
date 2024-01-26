import numpy as np
import copy



class Closed_Branch:
    def __init__(
            self,
            checks : np.array,
            events : np.array
    ):
        self.checks = checks
        self.events = events



    def add_check_to_closed_branch(self, new_check: int):
        assert self.checks[new_check] != 1, "Check already flipped for this closed branch"
        self.checks[new_check] = 1
    
    def add_event_to_closed_branch(self, new_event: int):
        self.events[new_event] = (1 + self.events[new_event]) % 2


class Cluster:
    def __init__(
            self,
            checks : np.array, # Inputs necesarios para ver el tamaño del código.
            events : np.array,
            closed_branches_1 : list = [],
            closed_branches_2 : list = []
    ):
        self.checks = checks
        self.events = events
        self.closed_branches_1 = closed_branches_1
        self.closed_branches_2 = closed_branches_2

    def add_check_to_cluster(self, new_check : np.array):
        assert np.all(self.checks[np.where(new_check == 1)[0]] != 1), "Check already flipped for this cluster"
        # self.checks[np.where(new_check == 1)[0]] = 1
        self.checks = np.bitwise_xor(self.checks.astype(np.uint8), new_check.astype(np.uint8))
    
    def add_event_to_cluster(self, new_event : np.array):
        # self.events[new_event] = (1 + self.events[new_event]) % 2
        self.events = np.bitwise_xor(self.events.astype(np.uint8), new_event.astype(np.uint8)) 

    def check_if_check_in_clusters_cbs(self, check : int ) -> bool:
        if not np.isin(check, np.where(self.checks == 1)[0]):
            return False
        else:
            return True

    def deletable_check(self, check: int) -> bool:
        """
        A check within the cluster is deletable if it is in closed_brances_2 (for destroying branch growth)
        """
        condition = False
        for closed_branch in self.closed_branches_2:
            if closed_branch.checks[check] == 1:
                return True
        return condition

    def delete_closed_branch_from_cluster(self, check : int):
        assert np.isin(check, np.where(self.checks == 1)[0]), " Check not in the closed branch from the clsuter."
        triggered_branch = [branch for branch in self.closed_branches_2 if branch.checks[check] == 1]
        if len(triggered_branch) != 1:
            pass
        assert len(triggered_branch) == 1, "There are more than one closed_branch related to the same check."
        self.checks[np.where(triggered_branch[0].checks == 1)[0]] = 0 
        self.events[np.where(triggered_branch[0].events == 1)[0]] = (self.events[np.where(triggered_branch[0].events == 1)[0]] + 1) % 2
        self.closed_branches_2.remove(triggered_branch[0])

    def include_closed_branch_to_cluster(self, closed_branch : Closed_Branch, pc : bool = False):
        # Make sure that it is not included if it shares checks with any other Closed_branch within the cluster.
        if pc:
            self.closed_branches_1.append(closed_branch)
        else:
            self.closed_branches_2.append(closed_branch)

class Branch:
    def __init__(
            self,
            pcm : np.ndarray,
            checks : np.array,
            events : np.array,
            check_to_search : int,
            weight_to_consider : float,
            clusters_to_consider: Cluster,
            sepd: list,
            sepc: list,
            ptbf : int,
            data : bool, # Añadir datas para hacer distinción entre matrices sparse
    ):
        self.pcm = pcm
        self.checks = checks
        self.events = events
        self.check_to_search = check_to_search
        self.weight_to_consider = weight_to_consider
        self.cluster = clusters_to_consider
        self.sepd = sepd
        self.sepc = sepc
        self.ptbf = ptbf
        self.m, self.n = self.pcm.shape
        self.data = data

    

    def grow_branch(
            self,
            llrs: np.array,
            syndrome : np.array,
            destruction : bool,
        ) -> list:
        """
        Growth of a branch instance which are not closed.

        Parameters
        ----------
        # number_of_growths : int
        #     The number of growths that we will consider.

        llrs : np.array
            Vector containing the llr values for every event within the pcm.

        syndrome: np.array
            Vector containing the non-trivial checks.

        destruction: bool,
            if True, it destroys other closed_branches in its path belonging to clusters_to_consider_2. If not, it does not consider those checks.

        Returns
        -------
        list  :
            List of Branches being instances the grown branch.
        """
        
        for sep in self.sepd:
            if len(sep) < 2:
                pass
        new_branches = []

        if not self.data:
            # Iterate over the self.pcm
            row_value = self.pcm.getrow(self.check_to_search).toarray().flatten()
        else:
            row_value = self.pcm[self.check_to_search]
        # result_columns = [index for index, value in enumerate(row_value) if value == 1] #=> columnas en las que actua el check trivial.
        result_columns = np.argwhere(row_value) #=> columnas en las que actua el check trivial.


        for sep in self.sepd:
            assert len(sep) > 1, 'Error en sepd'

        for col_index in result_columns:

            # Omit columns which are already on the branch

            if llrs[col_index] > self.weight_to_consider:
                continue
            else:
                weight_new = self.weight_to_consider - llrs[col_index]

            # Dentro de un cluster se pueden repetir eventos, pero dentro de una rama no.
            if self.events[col_index] == 1:
                continue
            
            check_nodes = np.zeros(self.m)
            new_event = np.zeros(self.n)
            new_event[col_index] = 1
            cluster_new_branch = copy.deepcopy(self.cluster)

            # Si es destructivo, mira al check to search. Si no lo es, procede as usual.
            if destruction and cluster_new_branch.deletable_check(self.check_to_search): # Condiciones suficientes para destruir.
                # La condición es que el crecimiento sea destructivo y que el check to search forme parte de un closed branch
                # no destructivo.
                triggered_branch = [branch for branch in cluster_new_branch.closed_branches_2 if branch.checks[self.check_to_search] == 1]
                assert len(triggered_branch) == 1, "There are more than one closed_branch related to the same check."
                cluster_new_branch.delete_closed_branch_from_cluster(self.check_to_search)
                # Dentro de la columna, los checks que corresponden a elementos no triviales:
                check_nodes = np.zeros(self.m)
                # We should first check if the check to search is in new_ones_indices
                check_nodes[self.check_to_search] = 1 
                # Los que corresponden a elementos triviales.
                checks_to_search = []
                check_to_add = np.zeros(self.pcm.shape[0])
                check_to_add[self.check_to_search] = 1
                cluster_new_branch.add_check_to_cluster(check_to_add)


            else:
                checks_to_flip = np.bitwise_xor(self.cluster.checks.astype(np.uint8), syndrome.astype(np.uint8))

                ones_indices = np.where(checks_to_flip == 1)[0]


                # Miro a ver si el resto de números de la columna están en el síndrome
                if not self.data:
                    non_trivial_indices = np.where(self.pcm[:, col_index].toarray() == 1)[0]
                else:
                    non_trivial_indices = np.where(self.pcm[:, col_index] == 1)[0]
                # Eliminamos el check to search.
                non_trivial_indices = np.delete(non_trivial_indices, np.where(non_trivial_indices == self.check_to_search)[0])


                # Dentro de la columna, los checks que corresponden a elementos no triviales:
                check_nodes[np.intersect1d(non_trivial_indices, ones_indices)] = 1
                # Los que corresponden a elementos triviales.
                checks_to_search = np.setdiff1d(non_trivial_indices, ones_indices)



                cluster_new_branch.add_check_to_cluster(check_nodes)
                cluster_new_branch.add_event_to_cluster(new_event)

            #  We redefine the new_event so as to place it in the overall branch
            new_event = self.events.copy()
            new_event[col_index] = (new_event[col_index] + 1) % 2
            
            # We must now decide what to do depending of the number of values in check_to_search.
            if len(checks_to_search) == 0: # Closed branch
                new_branch = Branch(
                    pcm = self.pcm,
                    checks = np.bitwise_xor(self.checks.astype(np.uint8), check_nodes.astype(np.uint8)),
                    # events = np.bitwise_xor(self.events.astype(np.uint8), new_event.astype(np.uint8)),
                    events = new_event,
                    check_to_search = -1,
                    weight_to_consider = weight_new,
                    clusters_to_consider  = cluster_new_branch,
                    sepd = self.sepd,
                    sepc = self.sepc,
                    ptbf = 0,
                    data = self.data
                )
                new_branches.append(new_branch)
            
            elif len(checks_to_search) == 1: # Branch continues in one direction
                new_branch = Branch(
                    pcm = self.pcm,
                    checks = np.bitwise_xor(self.checks.astype(np.uint8), check_nodes.astype(np.uint8)),
                    events = new_event,
                    # events = np.bitwise_xor(self.events.astype(np.uint8), new_event.astype(np.uint8)),
                    check_to_search = int(checks_to_search),
                    weight_to_consider = weight_new,
                    clusters_to_consider  = cluster_new_branch,
                    sepd = self.sepd,
                    sepc = self.sepc,
                    ptbf = self.ptbf,
                    data = self.data
                )
                new_branch.consider_loops()
                new_branches.append(new_branch)
            
            else: # Branch continues in several directions
                new_branch = Branch(
                    pcm = self.pcm,
                    checks = np.bitwise_xor(self.checks.astype(np.uint8), check_nodes.astype(np.uint8)),
                    events = new_event,
                    # events = np.bitwise_xor(self.events.astype(np.uint8), new_event.astype(np.uint8)),
                    check_to_search = int(checks_to_search[0]),
                    weight_to_consider = weight_new,
                    clusters_to_consider  = cluster_new_branch,
                    sepd = self.sepd + [list(checks_to_search)],
                    sepc = self.sepc + [int(checks_to_search[0])],
                    ptbf = self.ptbf,
                    data = self.data
                )
                for sep in new_branch.sepd:
                    if len(sep) < 2:
                        pass
                for i in range(len(new_branch.sepc)):
                    if not new_branch.sepc[i] in new_branch.sepd[i]:
                        new_branch.sepd[i].append(new_branch.sepc[i])
                new_branch.consider_loops()
                new_branches.append(new_branch)

            if new_branch.check_if_branch_is_closed():
                return [new_branch]

        if len(new_branches) == 0:
            return new_branches

        weight_values = [branch.separation_number() for branch in new_branches]
        threshold = min(weight_values)

        final_branches = [branch for branch in new_branches if weight_values[new_branches.index(branch)] == threshold and branch.weight_to_consider > min(llrs)]

        return final_branches


    def check_if_branch_is_closed(self):
        # Mirar los casos en los que ptbf son 0. Si no hay sepds se ha encontrado una rama cerrada. Esta función se hará dos veces.
        if self.ptbf != 0:
            return False
        else:
            if len(self.sepd) == 0:
                return True
            else:
                assert len(self.sepd[-1]) > 1, 'Sepd tiene longitud incorrecta'
                new_separation = []
                # If sepd is len() == 2, it is completely destroyed, if it is of higher length only one part is.
                for path in self.sepd[-1]:
                    if path != self.sepc[-1]:
                        new_separation.append(path)
                del self.sepd[-1]
                del self.sepc[-1]
                if len(new_separation) == 1:
                    self.ptbf = 1
                    self.check_to_search = new_separation[0]
                # Will only consider one of the paths for the separation. Once it is closed, it will consider the other one. This will reduce overhead.
                elif len(new_separation) > 1:
                    self.sepd.append(new_separation)
                    self.sepc.append(new_separation[0])
                    self.ptbf = 1
                    self.check_to_search = new_separation[0]
                # assert len(new_separation) > 0, 'An error has been produced, empty separation.'
                # for sep in self.sepd:
                #     assert len(sep) > 1, 'Fallo de sepd'
                # for i in range(len(self.sepc)):
                #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                return False
    
    def consider_loops(self):
        # TODO, considerar caso en el que varios loops se cierran de golpe. Una rama termina en separación y todos los elementos de la separación cierran loops.
        # Consider loops within the recently grown branches.

        if self.ptbf != 0:
            # cts = self.check_to_search
            # sepc = self.sepc
            # sepd = self.sepd
            for index, separation in enumerate(self.sepd):
                if self.check_to_search in separation and self.check_to_search != self.sepc[index]:
                    # Sufficient condition that there is a loop.
                    if len(self.sepd) == 1: # Only one separation
                        if len(self.sepd[index]) == 2:
                            self.check_to_search = -1
                            self.sepd = []
                            self.sepc = []
                            self.ptbf = 0
                            break
                        elif len(self.sepd[index]) == 3:
                            self.check_to_search = [element for element in self.sepd[index] if element != self.check_to_search and element != self.sepc[index]][0]
                            self.sepd = []
                            self.sepc = []
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            break
                        else:
                            # new_separation = [x for x in self.sepd[index] if x != self.sepc[index] and x != self.check_to_search]
                            self.sepd = [[x for x in self.sepd[index] if x != self.sepc[index] and x != self.check_to_search]]
                            self.sepc = [[x for x in self.sepd[index] if x != self.sepc[index] and x != self.check_to_search][0]]
                            self.check_to_search = [x for x in self.sepd[index] if x != self.sepc[index] and x != self.check_to_search][0]
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break
                    
                    # Considerando sepds con longitud más larga que 1, la última separación sepd[-1] cierra una separación anterior sepd[i].
                    # Tenemos que sacar cts[-1] y cts[i].
                    # Tenemos que considerar los siguientes casos:
                    # len(sepd[-1]) = len(sepd[i]) = 2 => eliminamos sepd[i] y sepd[-1] y el camino sigue por el camino sepd[-1] que no es sepc[-1].
                    # len(sepd[-1]) > 2 and len(sepd[i]) = 2 => eliminamos sepd[i] y sepc[i] y reducimos la separación sepd[-1], quitándole sepc[-1].
                    # len(sepd[-1]) = 2 and len(sepd[i]) > 2 => sacamos el sepc[i] de sepd[i] y eliminamos sepd[-1], haciendo que la rama siga por el otro lado.
                    # len(sepd[-1]) > 2 and len(sepd[i]) > 2 => sacamos sepc[i] y sepc[-1] de sepd[i] y sepc[-1] respectivamente. Y añadimos el resto de ramas por las que va sepd[-1].

                    # TODO mirar que pasa quan index == len(sepd) -1; possibilitat de tancar
                    # Se eliminan dos posibles caminos de la última separación.
                    elif index  == len(self.sepd) - 1:
                        if len(self.sepd[index]) == 2:
                            sepd_og = copy.deepcopy(self.sepd)
                            sepc_og = copy.deepcopy(self.sepc)
                            del self.sepd[-1]
                            del self.sepc[-1]
                            self.check_to_search = [path for path in self.sepd[-1] if path != self.sepc[-1]][0]
                            del self.sepd[-1][self.sepd[-1].index(self.sepc[-1])]
                            del self.sepc[-1]
                            self.sepc.append(self.check_to_search)
                            if len(self.sepd[-1]) == 1:
                                del self.sepd[-1]
                                del self.sepc[-1]
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # for sep in self.sepd:
                            #     if len(sep) < 2:
                            #         pass
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break
                        elif len(self.sepd[index]) == 3:
                            self.check_to_search = [path for path in self.sepd[-1] if path != self.sepc[-1]][0]
                            del self.sepd[-1]
                            del self.sepc[-1]
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # if len(sep) < 2:
                            #     pass
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break
                        elif len(self.sepd[index]) > 3:
                            self.check_to_search = [path for path in self.sepd[-1] if path != self.sepc[-1]][0]
                            del self.sepd[-1][self.sepd[-1].index(self.sepc[-1])]
                            del self.sepc[-1]
                            self.sepc.append(self.check_to_search)
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break

                    # TODO Paso peligroso, Tenemos que escoger otro sepc[index] por el que crecer si se junta 
                    else:
                        if len(self.sepd[-1]) == len(self.sepd[index]) == 2:
                            ogsepd = copy.deepcopy(self.sepd)
                            ogsepc = copy.deepcopy(self.sepc)
                            ogcts = copy.deepcopy(self.check_to_search)
                            self.check_to_search = [path for path in self.sepd[-1] if path != self.sepc[-1]][0]
                            del self.sepd[index]
                            del self.sepd[-1]
                            del self.sepc[index]
                            del self.sepc[-1]
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break
                        elif len(self.sepd[-1]) > 2 and len(self.sepd[index]) == 2:
                            self.check_to_search = [path for path in self.sepd[-1] if path != self.sepc[-1]][0]
                            del self.sepd[index]
                            del self.sepd[-1][self.sepd[-1].index(self.sepc[-1])]
                            del self.sepc[index]
                            del self.sepc[-1]
                            self.sepc.append(self.check_to_search)
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break
                        elif len(self.sepd[-1]) == 2 and len(self.sepd[index]) > 2:
                            del self.sepd[index][self.sepd[index].index(self.check_to_search)]
                            self.check_to_search = [path for path in self.sepd[-1] if path != self.sepc[-1]][0]
                            del self.sepd[-1]
                            del self.sepc[-1]
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break
                        # CHECK mirar amb atenció aquestes linies, és important tenir en compte el que passa.
                        elif len(self.sepd[-1]) > 2 and len(self.sepd[index]) > 2:
                            del self.sepd[index][self.sepd[index].index(self.check_to_search)]
                            self.check_to_search = [path for path in self.sepd[-1] if path != self.sepc[-1]][0]
                            del self.sepd[-1][self.sepd[-1].index(self.sepc[-1])]
                            del self.sepc[-1]
                            self.sepc.append(self.check_to_search)
                            # assert len(self.sepd) == len(self.sepc), 'Sepc and sepc have different lengths'
                            # assert self.check_to_search != -1, 'Check to search indicates closure, but branch is open'
                            # for sep in self.sepd:
                            #     assert len(sep) > 1, 'Fallo de sepd'
                            # for i in range(len(self.sepc)):
                            #     assert self.sepc[i] in self.sepd[i], 'Fallo, sepc no correspondiente a sepd'
                            self.consider_loops()
                            break
                        else:
                            print('There has been an error') # TODO arreglar errores que salen de aquí
                            print(f'Sepd {self.sepd}')
                            print(f'Sepc {self.sepc}')
                            print(f'CTS {self.check_to_search}')
                            print('\n')
                        

    def separation_number(self) -> int:
        """
        Number of outcoming branches from a branch.
        """
        sep_numb = 0
        for path in self.sepd:
            sep_numb += len(path)
        return sep_numb
    
