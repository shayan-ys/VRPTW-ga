from chromosome import Chromosome as BaseChromosome
from nodes import Deport, Customer, CustomerDistanceTable
from selections import selection_tournament_deterministic
from crossovers import crossover_uox, crossover_cx
from mutations import mutation_inversion
import ga_params
import utils

import matplotlib.pyplot as plt
from typing import List
from random import shuffle
import re


class Chromosome(BaseChromosome):
    @staticmethod
    def get_distance(source: int, dest: int) -> float:
        global customers_distance_table     # type: CustomerDistanceTable
        return customers_distance_table.get_distance(source, dest)

    @staticmethod
    def get_node(index: int) -> Customer:
        global customers
        return customers[index]


List_Chromosome = List[Chromosome]


class Population:
    generation = []     # type: List_Chromosome
    gen_index = 0   # type: int
    pop_size = 0    # type: int
    chromosome_width = 0    # type: int
    chromosome_higher_value_fitter = False
    crossover_method = staticmethod(crossover_cx)
    mutation_method = staticmethod(mutation_inversion)  # type: staticmethod
    removing_method = staticmethod(selection_tournament_deterministic)
    selection_method = staticmethod(selection_tournament_deterministic)
    selection_pressure = 2  # tournament size (k)
    selection_repeat = True
    parent_selection_ratio = 0.8
    mutation_ratio = 0.1
    genocide_ratio = 0.2
    # plot
    plot_x_axis = []
    plot_y_axis = []
    plot_x_div = 100
    plot_x_window = 100
    plot_fig = None
    plot_subplot = None

    def __init__(self, size: int, chromosome_width: int):
        self.pop_size = size
        self.chromosome_width = chromosome_width
        self.generation = self.initial_generation()
        plt.ion()
        self.fig, self.subplot = plt.subplots()
        self.fig2, self.subplot2 = plt.subplots()

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
        for parent1, parent2 in utils.couples(selected_parents):
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
        while self.gen_index < ga_params.MAX_GEN:
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
        plt.figure(1)
        min_generation = min(self.generation)   # type: Chromosome
        self.plot_x_axis.append(self.gen_index)
        self.plot_y_axis.append(min_generation.value)
        self.plot_x_axis = self.plot_x_axis[-self.plot_x_window:]
        self.plot_y_axis = self.plot_y_axis[-self.plot_x_window:]
        self.subplot.set_xlim([self.plot_x_axis[0], self.plot_x_axis[-1]])
        self.subplot.set_ylim([min(self.plot_y_axis) - 5, max(self.plot_y_axis) + 5])
        plt.suptitle('Best solution so far: ' + re.sub("(.{64})", "\\1\n", str(min_generation), 0, re.DOTALL),
                     fontsize=10)
        print(min_generation)
        self.subplot.plot(self.plot_x_axis, self.plot_y_axis)

        plt.figure(2)
        for route_x, route_y in min_generation.plot_get_route_cords():
            plt.plot(route_x, route_y)
        plt.draw()
        self.fig.savefig("plot-output.png")
        self.fig2.savefig("plot2-output.png")
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

from test_data import R101

customers = []
de = R101['deport']
de_cord = de['coordinates']
customers.append(Deport(de_cord['x'], de_cord['y'], de['due_time']))

for key, c in R101.items():
    if 'customer' in key:
        try:
            cord = c['coordinates']
            customers.append(Customer(cord['x'], cord['y'], c['demand'], c['ready_time'], c['due_time'],
                                      c['service_time']))
        except:
            pass

# print(len(customers))

customers_distance_table = CustomerDistanceTable(customers)
# print(str(customers_distance_table))

ga_pop = Population(100, len(customers))
# print(str(ga_pop))
best_chrome = ga_pop.evolve()
print(best_chrome)
