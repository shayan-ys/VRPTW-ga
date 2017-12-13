from chromosome import Chromosome as BaseChromosome
import population
from nodes import Deport, Customer, CustomerDistanceTable
from csv_reader import csv_read
import ga_params


class Chromosome(BaseChromosome):
    @staticmethod
    def get_distance(source: int, dest: int) -> float:
        global customers_distance_table     # type: CustomerDistanceTable
        return customers_distance_table.get_distance(source, dest)

    @staticmethod
    def get_node(index: int) -> Customer:
        global customers
        return customers[index]


population.Chromosome = Chromosome


customers_input_read = csv_read(ga_params.run_file['name'], header_map=ga_params.run_file['header_map'])
customers = [Deport(**customers_input_read[0])]
customers += [Customer(**customer_dict) for customer_dict in customers_input_read]
# for c in customers:
#     print(c)
# print(len(customers))

customers_distance_table = CustomerDistanceTable(customers)
# print(str(customers_distance_table))

ga_pop = population.Population(chromosome_width=len(customers), **ga_params.population)
# print(str(ga_pop))
best_chrome = ga_pop.evolve()
print(best_chrome)
