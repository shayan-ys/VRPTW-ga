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
    fitness = None  # type: float

    def __init__(self, route: list):
        self.route = route
        self.fitness = self.get_fitness()

    @staticmethod
    def get_travel_cost(c1: int, c2: int) -> float:
        global customers_travel_cost_table
        return customers_travel_cost_table[c1][c2]

    def get_fitness(self) -> float:
        fitness_holder = 0
        for c_first, c_second in pairwise(self.route):
            fitness_holder += self.get_travel_cost(c_first, c_second)
        return fitness_holder

    def __str__(self):
        return str(self.route) + " fitness= " + str(self.fitness)


class Population:
    generation = []     # type: list
    gen_index = 0   # type: int
    size = 0    # type: int
    chromosome_width = 0    # type: int

    def __init__(self, size: int, chromosome_width: int):
        self.size = size
        self.chromosome_width = chromosome_width
        self.initial_generation()

    def initial_generation(self):
        random_indices = list(range(self.chromosome_width))
        for i in range(self.size):
            shuffle(random_indices)
            init_chromosome = Chromosome(random_indices)
            self.generation.append(init_chromosome)

    def __str__(self):
        pop_str = "Generation:" + str(self.gen_index) + '\n'
        for i, chromosome in enumerate(self.generation):
            pop_str += str(i + 1) + ': ' + str(chromosome) + '\n'

        return pop_str


customers = [
    Customer(35, 35),
    Customer(41, 49),
    Customer(35, 17),
    Customer(55, 45),
    Customer(55, 20),
]

customers_travel_cost_table = get_travel_cost_table_customers(customers, print_result=True)

ga_pop = Population(10, len(customers))
print(str(ga_pop))
