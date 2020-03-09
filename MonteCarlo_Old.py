"""
An implementation of the 'Discrete Adiabatic' Monte Carlo Sorting Algorithm
    (Smith 2016)
Algorithm citation: https://arxiv.org/pdf/1612.08555.pdf
"""

import random
from copy import copy, deepcopy
import datetime
import collections


class MonteCarlo:

    def __init__(self, data, p=.999, N=None, epsilon=1):
        self.original_data = data
        self.data_dictionary = dict(zip(range(len(data)), data))
        self.data = list(self.data_dictionary.keys())
        if p <= 0:
            p = .001
        self.p = p
        self.prob = (1 - self.p) / self.p
        self.length = len(self.data)
        if N is None:
            N = len(data) // 2  # Come back to this number, it's probably bad
        self.N = N
        self.N_array = dict(list())
        self.all_same = False
        self.data_n_disputes = {x: 0 for x in data}
        self.data_i_have_beaten = {x: set() for x in data}
        self.epsilon = epsilon  # 0 < epsilon << 1, lower is more accurate
        for i in range(N):
            success = False
            while not success:
                new_list = random.sample(self.data, len(self.data))
                success = True
                for each in self.N_array:
                    if new_list == self.N_array[each]:
                        success = False
            self.N_array[i] = new_list

    def next_pair(self):
        i, j = self._get_ij()
        return i, j

    def _get_ij(self):
        uncertain_i = 0
        uncertain_j = 0
        min_Nij_minus_Nji = 999999999999999999  # There's probably a more elegant way of doing this
        for i in self.data:
            for j in self.data:
                if i == j:
                    continue
                new_min = self._get_Nij_minus_Nji(i, j)
                if new_min < min_Nij_minus_Nji:
                    min_Nij_minus_Nji = new_min
                    uncertain_i = i
                    uncertain_j = j
                    if min_Nij_minus_Nji == 0:
                        return uncertain_i, uncertain_j
        return uncertain_i, uncertain_j

    def _get_Nij_minus_Nji(self, i, j):
        Nij = 0
        Nji = 0
        for each in self.N_array.values():
            if each.index(i) < each.index(j):
                Nij += 1
            else:
                Nji += 1
        return (Nij - Nji) ** 2

    def _is_i_less_than_j(self, i, j, target_list):
        if target_list.index(i) < target_list.index(j):
            return True
        else:
            return False

    def N_array_to_dictionary(self):
        pass
    """
    Potentially add this for better computational efficiency:
    { e: i for i, e in enumerate(a_list) }
    """

    def compare(self, pair, higher):
        # for higher: True = 0th higher, False = 1st higher
        if higher:
            self._process_compare(pair[0], pair[1])
        else:
            self._process_compare(pair[1], pair[0])
        if self._check_list_unity():
            self.all_same = True

    def _process_compare(self, higher, lower):
        self.data_n_disputes[lower] += 1
        self.data_i_have_beaten[higher].add(lower)
        for list_id in self.N_array:
            if self._is_i_less_than_j(lower, higher, self.N_array[list_id]):
                continue
            else:
                self._process_mismatch(higher, lower, list_id)

    def _process_mismatch(self, higher, lower, list_id):
        if self._decision(self.prob):
            return
        else:
            # self._max_element_sampling(higher, lower, list_id)
            self._max_element_refactored(higher, lower, list_id)

    def _max_element_sampling(self, higher, lower, list_id):  # Random shuffle is placeholder - come back and flush out
        print(f"entering max_element at: {datetime.datetime.now()}")
        lower_index = self.N_array[list_id].index(lower)
        higher_index = self.N_array[list_id].index(higher)
        lower_list = deepcopy(self.N_array[list_id][:higher_index])
        higher_list = deepcopy(self.N_array[list_id][lower_index + 1:])
        middle_list = deepcopy(self.N_array[list_id][higher_index:lower_index + 1])
        new_list = list()
        local_n_dispute = deepcopy(self.data_n_disputes)
        tries = 0
        while len(middle_list) > 1:
            tries = 0
            # "Select a single random element e_max uniformly from the list"
            e_max = middle_list[random.randint(0, len(middle_list) - 1)]
            # Accept e_max as the largest element w/ prob: ((1 - p) / p)**n_dispute
            prob = ((1 - self.p) / self.p) ** local_n_dispute[e_max]
            if self._decision(prob):
                tries = 0
                new_list.append(e_max)
                middle_list.remove(e_max)
                for lower_dat in self.data_i_have_beaten[e_max]:
                    if lower_dat in middle_list:
                        local_n_dispute[lower_dat] -= 1
            else:
                tries += 1
                # print(f"reject: {tries}", end='\r', flush=True)
        new_list.append(middle_list[0])

        new_list.reverse()

        self.N_array[list_id] = lower_list + new_list + higher_list
        print(f"\nexiting max_element at: {datetime.datetime.now()}")


        """lower_index = self.N_array[list_id].index(lower)
        higher_index = self.N_array[list_id].index(higher)
        lower_list = self.N_array[list_id][:higher_index]
        higher_list = self.N_array[list_id][lower_index + 1:]
        middle_list = self.N_array[list_id][higher_index:lower_index + 1]
        while middle_list.index(higher) < middle_list.index(lower):
            random.shuffle(middle_list)
        new_list = lower_list + middle_list + higher_list
        self.N_array[list_id] = new_list"""

    def _max_element_refactored(self, higher, lower, list_id):

        lower_index = self.N_array[list_id].index(lower)
        higher_index = self.N_array[list_id].index(higher)
        lower_list = deepcopy(self.N_array[list_id][:higher_index])
        higher_list = deepcopy(self.N_array[list_id][lower_index + 1:])
        middle_list = deepcopy(
            self.N_array[list_id][higher_index:lower_index + 1])
        new_list = list()

        while len(middle_list) > 1:
            w = 0
            i = 0
            sigma = random.random()

            beta_list = list()
            for element in middle_list:
                beta = ((1 - self.p) / self.p) ** self.data_n_disputes[element]
                beta_list.append(beta)

            Z = sum(beta_list)

            accepted_element = False

            while not accepted_element:
                gamma = beta_list[i] / Z
                if sigma < w + gamma:
                    new_list.append(middle_list[i])
                    accepted_element = True
                else:
                    w = w + gamma
                    i += 1
            middle_list.remove(middle_list[i])
        new_list.append(middle_list[0])
        new_list.reverse()

        self.N_array[list_id] = lower_list + new_list + higher_list

        x = 0

    def _check_list_unity(self):
        if self.epsilon == 1:
            unified = True
            zero_list = self.N_array[0]
            for each in self.N_array.values():
                if not zero_list == each:
                    unified = False
                    break
            return unified
        else:
            all_lists = [tuple(x) for x in self.N_array.values()]
            counter = collections.Counter(all_lists)
            most_common_list, most_common_int = counter.most_common(1)[0]
            f = most_common_int / self.N
            if f > 1 - self.epsilon:
                return True
            else:
                return False

    def _decision(self, probability):
        return random.random() < probability

    def get_sorted(self):
        return self.N_array[random.randint(0, self.N - 1)]

    def get_confidence(self):
        pass
