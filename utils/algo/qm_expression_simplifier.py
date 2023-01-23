import utils.data.str_join as j
import utils.algo.generic_combinatorics as gc
import utils.data.indexof as idxo
from utils.algo.merge_sort import merge_sort

# A minterm is a term in an arbitrary boolean expression which evaluates to 1. 
# It's represented by a binary number designating the argument values required to satisfy this condition (e.g. 011 for args a, b, c...)
class Minterm:
    # An implicant is a combination of minterms. Usually, it's expressed in decimals, but here, it's in binary
    def __init__(self, implicants: list[str], bin_value: str):
        self.bin_value = bin_value
        self.implicants = implicants
        self.comboed = False

        merge_sort(self.implicants) # needed for later comparisons
    
    def __str__(self):
        values = j.str_join([str(value) for value in self.implicants], ", ")[:-2]
        return "m(%s) = %s" % (values, self.bin_value)

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, minterm):
        if not isinstance(minterm, Minterm):
            return False

        return self.bin_value == minterm.bin_value and self.implicants == minterm.implicants

    # combine w/ other minterms to produce implicants (needed for prime implicant generation for algorithm)
    # when the maximum depth of combination for a given minterm is reached against all other minterms in adjacent groups (for an expression, this means all minterms grouped by numbers of 1s in them)
    # that minterm is called a "prime implicant", which is used in the prime implicant table for simplification generation
    def combine(self, minterm: 'Minterm'):
        if self.bin_value == minterm.bin_value or self.implicants == minterm.implicants:
            return None
        
        # in the algorithm, only a difference of ONE bit is permitted
        # if there is more than a 1-bit (e.g. insignificant) difference between 2 minterms, they cannot be combined
        diff = 0
        result = ""

        for idx in range(len(self.bin_value)):
            if self.bin_value[idx] != minterm.bin_value[idx]:
                diff += 1
                result += "-" # dashes represent differences in the algorithm
            else:
                result += self.bin_value[idx]
            
            if diff > 1:
                return None
        
        # if all is well, can combine these to form 1 minterm which encompasses both minterms' implicants
        # add new resulting binary val
        return Minterm(self.implicants + minterm.implicants, result)


# Binary expression simplifier using Quine-McCluskey algorithm
# https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm
class QMExpressionSimplifier:
    # Important: SOP rows should be converted to binary beforehand w/ bitshifting
    def simplify(self, allowed_args: list[str], sop_binary_rows: list[str]) -> list[Minterm]:
        allowed_arg_count = len(allowed_args)
        prime_implicants = self.__prime_implicants(allowed_arg_count, sop_binary_rows)
        
        # these are the prime implicants with which the expression cannot exist and be valid
        essential_prime_implicants = []
        comboed_rows = [False] * len(sop_binary_rows)

        for row in sop_binary_rows:
            row_uses = 0
            last_minterm_with_row_present = None
            for minterm in prime_implicants:
                if row in minterm.implicants:
                    row_uses += 1
                    last_minterm_with_row_present = minterm
            
            # exactly one use necessitates it's a prime implicate and required to be in the expression
            if row_uses == 1 and last_minterm_with_row_present not in essential_prime_implicants:
                for implicant in last_minterm_with_row_present.implicants:
                    comboed_rows[idxo.index_of(sop_binary_rows, implicant)] = True # mark all of these implicants as already comboed
                essential_prime_implicants.append(last_minterm_with_row_present)
        
        all_comboed = True
        for row in comboed_rows:
            if row == False:
                all_comboed = False
                break

        # means only prime implicants cover expression, therefore can return it
        if all_comboed:
            return essential_prime_implicants
            
        # remove the non-essential implicants
        prime_implicants = [prime_implicant for prime_implicant in prime_implicants if prime_implicant not in essential_prime_implicants]

        # one prime implicant remaining exit scenario
        if len(prime_implicants) == 1:
            return essential_prime_implicants + prime_implicants

        # otherwise, find the most minified solution through combinations
        non_essential_rows = [sop_binary_rows[index] for index in range(len(sop_binary_rows)) if not comboed_rows[index]]
        min_comb = self.__min_prime_implicant_combination(non_essential_rows, prime_implicants)
        if min_comb is None:
            return essential_prime_implicants
        return essential_prime_implicants + min_comb

    # group rows based on number of ones in binary
    def __initial_qm_group(self, allowed_arg_count: int, sop_binary_rows: list[str]):
        groups = [[] for _ in range(allowed_arg_count + 1)]
        for num in sop_binary_rows:
            cur_one_count = 0 
            for char in num:
                if char == "1":
                    cur_one_count += 1
            groups[cur_one_count].append(Minterm([num], num))
        
        return groups

    def __prime_implicants(self, allowed_arg_count: int, sop_binary_rows: list[str], groups: list[list[Minterm]] = None) -> list[Minterm]:
        if groups == None:
            groups = self.__initial_qm_group(allowed_arg_count, sop_binary_rows)

        # exit condition
        if len(groups) == 1:
            return groups[0]

        max_comboed_minterms = []
        comparison_count = range(len(groups) - 1) # because comparing only adjacents
        new_groups = [[] for _ in comparison_count]

        for comparison_idx in comparison_count:
            original = groups[comparison_idx]
            adjacent = groups[comparison_idx + 1]

            for or_term in original:
                for adj_term in adjacent:
                    combination = or_term.combine(adj_term)
                    if combination != None:
                        # mark as comboed upon successful combination
                        or_term.comboed = True
                        adj_term.comboed = True
                        if combination not in new_groups[comparison_idx]:
                            # new minterm won't be comboed
                            # that's how recursion satisfies this (eventually all will give NONE on combine attempt)
                            new_groups[comparison_idx].append(combination)
        
        # add current minterms to max_comboed_minterms (mostly for top-level recursion)
        for group in groups:
            for term in group:
                if not term.comboed and term not in max_comboed_minterms:
                    max_comboed_minterms.append(term)

        # use new groups to start calculating again and do more combinations
        for term in self.__prime_implicants(allowed_arg_count, sop_binary_rows, new_groups):
            if not term.comboed and term not in max_comboed_minterms:
                max_comboed_minterms.append(term)
        
        return max_comboed_minterms

    # returns the smallest combination set (minterm list) from prime implicants satisfies original SOP expression rows (e.g. minterms) which belong to the prime implicants
    def __min_prime_implicant_combination(self, prime_implicant_binary_rows: list[str], prime_implicants: list[Minterm]) -> list[Minterm]:
        prime_implicants = list(prime_implicants)
        prime_implicants_combinations = gc.combinations(prime_implicants)
        min_combination = None # list of minterms that is smallest
        for combination in prime_implicants_combinations:
            temp_combination: list[str] = []
            for term in combination:
                for implicant in term.implicants:
                    if implicant not in temp_combination and implicant in prime_implicant_binary_rows:
                        temp_combination.append(implicant)
            merge_sort(temp_combination)

            if temp_combination == prime_implicant_binary_rows:
                min_combination_l = 0 if min_combination is None else len(min_combination)
                if len(combination) < min_combination_l:
                    min_combination = combination
        
        return min_combination