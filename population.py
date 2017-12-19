import chromosome as chrome
from report import Reporter
import ga_params
import utils

from typing import List
from random import shuffle
from datetime import datetime
import numpy as np


class Chromosome(chrome.Chromosome):
    pass


List_Chromosome = List[Chromosome]


class Population(Reporter):
    generation = []     # type: List_Chromosome
    gen_index = 0   # type: int
    pop_size = None    # type: int
    chromosome_width = None    # type: int
    chromosome_higher_value_fitter = None
    crossover_method = None
    mutation_method = None
    removing_method = None
    selection_method = None
    selection_pressure = None  # tournament size (k)
    selection_repeat = None
    parent_selection_ratio = None
    mutation_ratio = None
    genocide_ratio = 0
    # plot
    x_axis = []
    y_axis = []
    gen_index_div = None    # type: int
    plot_x_div = None
    plot_x_window = None
    plot_fig = None
    plot_subplot = None
    chromosome_class = None

    def __init__(self, pop_size: int, chromosome_width: int, run_file_name: str,
                 crossover_method: staticmethod, mutation_method: staticmethod,
                 removing_method: staticmethod, selection_method: staticmethod,
                 selection_pressure: int, selection_repeat: bool,
                 parent_selection_ratio: float, mutation_ratio: float, elitism_count: int=0,
                 gen_index_div: int=50, plot_x_div: int=200, plot_x_window: int=400):
        self.pop_size = int(pop_size)
        self.chromosome_width = int(chromosome_width)
        self.chromosome_higher_value_fitter = Chromosome.higher_value_fitter
        self.crossover_method = crossover_method.__func__
        self.mutation_method = mutation_method.__func__
        self.removing_method = removing_method.__func__
        self.selection_method = selection_method.__func__
        self.selection_pressure = 2 if selection_pressure is None else int(selection_pressure)
        self.selection_repeat = bool(selection_repeat)
        self.parent_selection_ratio = float(parent_selection_ratio)
        self.mutation_ratio = float(mutation_ratio)
        self.elitism_count = elitism_count
        self.plot_x_div = int(plot_x_div)
        self.gen_index_div = int(gen_index_div)
        self.plot_x_window = int(plot_x_window)

        self.generation = self.initial_generation()
        super(Population, self).__init__(run_name=run_file_name)

    def initial_generation(self, init_size: int=None) -> List_Chromosome:
        if not init_size:
            init_size = self.pop_size
        generation_holder = []
        random_indices = list(range(1, self.chromosome_width))
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

    def elitism(self, generation: list) -> list:
        elites = []
        gen = list(generation)     # copy to make sure the generation itself doesn't change
        for i in range(self.elitism_count):
            best = min(gen)
            gen.remove(best)
            elites.append(best)
        return elites

    def next_gen(self) -> List_Chromosome:
        # create new offsprings by crossover
        children = self.get_offsprings(self.generation)
        # new children added to the population
        new_gen = self.generation + children    # type: List_Chromosome
        # permutation on the whole population
        self.permute_generation(new_gen)
        # apply elitism
        new_gen += self.elitism(self.generation)
        # defined pop_size - current population size should be removed using reversed tournament selection
        deceasing_size = max(len(new_gen) - self.pop_size, 0)
        self.remove_less_fitters(new_gen, deceasing_size)
        return new_gen

    def evolve(self) -> Chromosome:
        process_timer_start = datetime.now()
        while self.gen_index < ga_params.MAX_GEN:
            if self.gen_index % self.gen_index_div == 0:
                process_time = datetime.now() - process_timer_start
                process_timer_start = datetime.now()
                if ga_params.print_benchmarks:
                    print('### Process time of ' + str(self.gen_index_div) + ' generation: '
                          + str(process_time))
                self.report(process_time)
                if self.genocide_ratio > 0 and min(self.generation).value == max(self.generation).value:
                    self.generation = self.genocide(self.generation)
            self.generation = self.next_gen()
            self.gen_index += 1
        return min(self.generation)

    def report(self, process_time=None):

        self.x_axis.append(self.gen_index)
        self.y_axis.append({
            'best': min(self.generation),
            'worst': max(self.generation),
            'average': sum(self.generation) / len(self.generation),
            'std': np.std(self.generation),
            'process_time': process_time
        })
        if self.gen_index % self.plot_x_div:
            if ga_params.draw_plot:
                plot_process_timer_start = datetime.now()
                self.plot_draw(x_axis=self.x_axis, y_axis=self.y_axis, latest_result=min(self.generation))
                if ga_params.print_benchmarks:
                    print('### Plot time: ' + str(datetime.now() - plot_process_timer_start))
            if ga_params.export_spreadsheet:
                self.export_spreadsheet(x_axis=self.x_axis, y_axis=self.y_axis)
            self.x_axis = []
            self.y_axis = []

    def genocide(self, generation: List_Chromosome):
        new_gen_size = int(len(generation) * self.genocide_ratio)
        surviving_selection_size = len(generation) - new_gen_size
        # noinspection PyCallingNonCallable
        survivors = self.selection_method(generation, surviving_selection_size, k=self.selection_pressure,
                                          repeat=self.selection_repeat,
                                          reverse=(not self.chromosome_higher_value_fitter))
        new_gen = self.initial_generation(new_gen_size)
        return survivors + new_gen

    def __str__(self):
        pop_str = "Generation:" + str(self.gen_index) + '\n'
        for i, chromosome in enumerate(self.generation):
            pop_str += str(i + 1) + ': ' + str(chromosome) + '\n'
        return pop_str

    def __repr__(self):
        return self.__str__()