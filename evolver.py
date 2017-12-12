from selections import selection_tournament_deterministic
from crossovers import crossover_uox, fill_remaining
from mutations import mutation_inversion

from datetime import datetime
from typing import List
from random import shuffle
import math

PRINT_BENCHMARKS = False


def pairwise(a: list) -> iter:
    """
    Iterate list items two by two
    Source: https://stackoverflow.com/a/5764948/4744051
    :param a: Given list, e.g.: a = [5, 7, 11, 4, 5]
    :return: Iterable pairs: [5, 7], [7, 11], [11, 4], [4, 5]
    """
    return zip(a[:-1], a[1:])


def couples(iterable):
    """
    Iterate over pairs (even-odd)
    :param iterable: s = s0, s1, s2, s3, s4, s5, ...
    :return: (s0, s1), (s2, s3), (s4, s5), ...
    """
    a = iter(iterable)
    return zip(a, a)


class Customer:
    x = None    # type: int
    y = None    # type: int

    def __init__(self, x_coordinates: int, y_coordinates: int):
        self.x = x_coordinates
        self.y = y_coordinates


List_Customer = List[Customer]


def get_travel_cost_customers_pair(c1: Customer, c2: Customer) -> float:
    return math.hypot(c2.x - c1.x, c2.y - c1.y)


def get_travel_cost_table_customers(customer_list: List_Customer, print_result: bool=False) -> list:
    global PRINT_BENCHMARKS
    cost_table_timer = datetime.now()

    cost_table_holder = []

    for needle_index, customer_needle in enumerate(customer_list):

        cost_table_holder.append([])
        for in_stack_index, customer_in_stack in enumerate(customer_list):

            if needle_index == in_stack_index:
                cost = 0
            elif needle_index > in_stack_index:
                cost = cost_table_holder[in_stack_index][needle_index]
            else:
                cost = get_travel_cost_customers_pair(customer_needle, customer_in_stack)

            cost_table_holder[needle_index].append(cost)

    if PRINT_BENCHMARKS:
        print('--- distance table pre-computation time: ' + str(datetime.now() - cost_table_timer))

    if print_result:
        print("--- Travel Cost between Customers")
        for row in cost_table_holder:
            print(row)
        print("--- END | Travel Cost Between Customers")

    return cost_table_holder


class Chromosome:
    route = []      # type: list
    value = None  # type: float

    def __init__(self, route: iter):
        self.route = list(route)
        self.value = self.get_value()

    @staticmethod
    def get_travel_cost(c1: int, c2: int) -> float:
        global customers_travel_cost_table
        return customers_travel_cost_table[c1][c2]

    def get_value(self) -> float:
        value_holder = 0
        for c_first, c_second in pairwise(self.route):
            value_holder += self.get_travel_cost(c_first, c_second)
        return value_holder

    def __iter__(self):
        for r in self.route:
            yield r

    # def __gt__(self, other):
    #     return self.value > other.value

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.route) + " value= " + str(self.value)

    def __repr__(self):
        return self.__str__()


List_Chromosome = List[Chromosome]


class Population:
    generation = []     # type: List_Chromosome
    gen_index = 0   # type: int
    pop_size = 0    # type: int
    chromosome_width = 0    # type: int
    chromosome_higher_value_fitter = False
    crossover_method = staticmethod(crossover_uox)
    mutation_method = staticmethod(mutation_inversion)  # type: staticmethod
    removing_method = staticmethod(selection_tournament_deterministic)
    selection_method = staticmethod(selection_tournament_deterministic)
    selection_pressure = 2  # tournament size (k)
    selection_repeat = True
    parent_selection_ratio = 0.8
    mutation_ratio = 0.1

    def __init__(self, size: int, chromosome_width: int):
        self.pop_size = size
        self.chromosome_width = chromosome_width
        self.initial_generation()

    def initial_generation(self):
        random_indices = list(range(self.chromosome_width))
        for i in range(self.pop_size):
            shuffle(random_indices)
            init_chromosome = Chromosome(random_indices)
            self.generation.append(init_chromosome)

    def crossover(self, parent1: Chromosome, parent2: Chromosome) -> (Chromosome, Chromosome):
        # noinspection PyCallingNonCallable
        indices1, indices2 = self.crossover_method(list(parent1), list(parent2))
        child1 = Chromosome(indices1)
        child2 = Chromosome(indices2)
        return child1, child2

    def mutation(self, chromosome: Chromosome) -> Chromosome:
        # noinspection PyCallingNonCallable
        muted_indices = self.mutation_method(list(chromosome))
        return Chromosome(muted_indices)

    def parent_selection(self, generation: List_Chromosome) -> list:
        parent_selection_size = int(len(generation) * self.parent_selection_ratio)
        # noinspection PyCallingNonCallable
        return self.selection_method(generation, parent_selection_size, k=self.selection_pressure,
                                     repeat=self.selection_repeat, reverse=(not self.chromosome_higher_value_fitter))

    def mutation_index_selection(self, generation: List_Chromosome) -> list:
        mutation_selection_size = int(len(generation) * self.mutation_ratio)
        indices = list(range(len(generation)))
        shuffle(indices)
        return indices[:mutation_selection_size]

    def get_offsprings(self, generation: List_Chromosome) -> List_Chromosome:
        selected_parents = self.parent_selection(generation)
        offsprings_holder = []
        for parent1, parent2 in couples(selected_parents):
            child1, child2 = self.crossover(parent1, parent2)
            offsprings_holder += [child1, child2]
        return offsprings_holder

    def permute_generation(self, generation: List_Chromosome):
        mutation_indices = self.mutation_index_selection(generation)
        for index in mutation_indices:
            generation[index] = self.mutation(generation[index])

    def remove_less_fitters(self, generation: List_Chromosome, removing_size: int):
        # noinspection PyCallingNonCallable
        selected_chromosomes = self.removing_method(generation, removing_size, k=self.selection_pressure,
                                                    repeat=False, reverse=self.chromosome_higher_value_fitter)
        for ch in selected_chromosomes:
            generation.remove(ch)

    def next_gen(self) -> List_Chromosome:
        # create new offsprings by crossover
        children = self.get_offsprings(self.generation)
        # new children added to the population
        new_gen = self.generation + children    # type: List_Chromosome
        # permutation on the whole population
        self.permute_generation(new_gen)
        # defined pop_size - current population size should be removed using reversed tournament selection
        deceasing_size = max(len(new_gen) - self.pop_size, 0)
        self.remove_less_fitters(new_gen, deceasing_size)
        return new_gen

    def evolve(self) -> Chromosome:
        global MAX_GEN
        while self.gen_index < MAX_GEN:
            self.generation = self.next_gen()
            self.gen_index += 1
        return min(self.generation)

    def __str__(self):
        pop_str = "Generation:" + str(self.gen_index) + '\n'
        for i, chromosome in enumerate(self.generation):
            pop_str += str(i + 1) + ': ' + str(chromosome) + '\n'
        return pop_str

    def __repr__(self):
        return self.__str__()


customers = [
    Customer(35, 35),
    Customer(41, 49),
    Customer(35, 17),
    Customer(55, 45),
    Customer(55, 20),
]

MAX_GEN = 100000

customers_travel_cost_table = get_travel_cost_table_customers(customers, print_result=True)

ga_pop = Population(10, len(customers))
print(str(ga_pop))
best_chrome = ga_pop.evolve()
print(best_chrome)

# [3, 1, 0, 2, 4] value= 68.01551440644553
