from selections import selection_tournament_deterministic
from crossovers import crossover_uox
from mutations import mutation_inversion

import matplotlib.pyplot as plt
from datetime import datetime
from typing import List
from random import shuffle
import math
import re

from test_data_deap import DEAP_gr17_distance_table

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
    parent_selection_ratio = 0.7
    mutation_ratio = 0.2
    genocide_ratio = 0.0
    # plot
    plot_x_axis = []
    plot_y_axis = []
    plot_x_div = 10
    plot_x_window = 10
    plot_fig = None
    plot_subplot = None

    def __init__(self, size: int, chromosome_width: int):
        self.pop_size = size
        self.chromosome_width = chromosome_width
        self.generation = self.initial_generation()
        plt.ion()
        self.fig, self.subplot = plt.subplots()

    def initial_generation(self, init_size: int=None) -> List_Chromosome:
        if not init_size:
            init_size = self.pop_size
        generation_holder = []
        random_indices = list(range(self.chromosome_width))
        for i in range(init_size):
            shuffle(random_indices)
            init_chromosome = Chromosome(random_indices)
            generation_holder.append(init_chromosome)
        return generation_holder

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
            if self.gen_index % self.plot_x_div == 0:
                self.plot_draw()
                if min(self.generation).value == max(self.generation).value:
                    self.generation = self.genocide(self.generation)
            self.generation = self.next_gen()
            self.gen_index += 1
        return min(self.generation)

    def genocide(self, generation: List_Chromosome):
        surviving_selection_size = int(len(generation) * self.parent_selection_ratio)
        new_gen_size = len(generation) - surviving_selection_size
        # noinspection PyCallingNonCallable
        survivors = self.selection_method(generation, surviving_selection_size, k=self.selection_pressure,
                                          repeat=self.selection_repeat,
                                          reverse=(not self.chromosome_higher_value_fitter))
        new_gen = self.initial_generation(new_gen_size)
        return survivors + new_gen

    def plot_draw(self):
        self.plot_x_axis.append(self.gen_index)
        self.plot_y_axis.append(min(self.generation).value)
        self.plot_x_axis = self.plot_x_axis[-self.plot_x_window:]
        self.plot_y_axis = self.plot_y_axis[-self.plot_x_window:]
        self.subplot.set_xlim([self.plot_x_axis[0], self.plot_x_axis[-1]])
        self.subplot.set_ylim([min(self.plot_y_axis) - 5, max(self.plot_y_axis) + 5])
        plt.suptitle('Best solution so far: ' + re.sub("(.{64})", "\\1\n", str(min(self.generation)), 0, re.DOTALL),
                     fontsize=10)
        self.subplot.plot(self.plot_x_axis, self.plot_y_axis)
        plt.draw()
        self.fig.savefig("plot-output.png")
        plt.pause(0.0001)

    def __str__(self):
        pop_str = "Generation:" + str(self.gen_index) + '\n'
        for i, chromosome in enumerate(self.generation):
            pop_str += str(i + 1) + ': ' + str(chromosome) + '\n'
        return pop_str

    def __repr__(self):
        return self.__str__()


# customers = [
#     Customer(35, 35),
#     Customer(41, 49),
#     Customer(35, 17),
#     Customer(55, 45),
#     Customer(55, 20),
# ]
customers = []

from test_data import R101

# for key, c_data in R101.items():
#     try:
#         cord = c_data['coordinates']
#         customers.append(Customer(cord['x'], cord['y']))
#     except:
#         pass

for i in range(17):
    customers.append(Customer(i, i))

# print(len(customers))

MAX_GEN = 100

# customers_travel_cost_table = get_travel_cost_table_customers(customers, print_result=False)
customers_travel_cost_table = DEAP_gr17_distance_table

ga_pop = Population(300, len(customers))
# print(str(ga_pop))
best_chrome = ga_pop.evolve()
print(best_chrome)
