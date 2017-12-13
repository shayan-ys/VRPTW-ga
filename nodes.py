import ga_params
from typing import List
from datetime import datetime
import math


class Customer:
    x = None             # type: int
    y = None             # type: int
    demand = None        # type: int
    ready_time = None    # type: int
    due_time = None      # type: int
    service_time = None  # type: int

    def __init__(self, x_coordinates: int, y_coordinates: int, demand: int, ready_time: int, due_time: int,
                 service_time: int, **kwargs):
        self.x = int(float(x_coordinates))
        self.y = int(float(y_coordinates))
        self.demand = int(float(demand))
        self.ready_time = int(float(ready_time))
        self.due_time = int(float(due_time))
        self.service_time = int(float(service_time))

    def __str__(self):
        return 'coordinated: ' + str(self.x) + ' - ' + str(self.y)\
               + ' | demand: ' + str(self.demand) + ' | ready_time: ' + str(self.ready_time)\
               + ' | due_time: ' + str(self.due_time) + ' | service_time: ' + str(self.service_time)

    def __repr__(self):
        return self.__str__()


List_Customer = List[Customer]


class Deport(Customer):
    def __init__(self, x_coordinates: int, y_coordinates: int, due_time: int, **kwargs):
        super(Deport, self).__init__(x_coordinates, y_coordinates, demand=0, ready_time=0, due_time=due_time,
                                     service_time=0)


def get_distance_customers_pair(c1: Customer, c2: Customer) -> float:
    return math.hypot(c2.x - c1.x, c2.y - c1.y)


class CustomerDistanceTable:
    distance_table = None   # type: list

    def get_distance(self, source: int, dest: int) -> float:
        return self.distance_table[source][dest]
    
    def __init__(self, customer_list: List_Customer):
        cost_table_timer = datetime.now()
        self.distance_table = []
    
        for needle_index, customer_needle in enumerate(customer_list):
    
            self.distance_table.append([])
            for in_stack_index, customer_in_stack in enumerate(customer_list):
    
                if needle_index == in_stack_index:
                    cost = 0
                elif needle_index > in_stack_index:
                    cost = self.distance_table[in_stack_index][needle_index]
                else:
                    cost = get_distance_customers_pair(customer_needle, customer_in_stack)
    
                self.distance_table[needle_index].append(cost)
    
        if ga_params.print_benchmarks:
            print('--- distance table pre-computation time: ' + str(datetime.now() - cost_table_timer))
    
    def __str__(self):
        table_str = "--- Travel Cost between Customers"
        for row in self.distance_table:
            table_str += str(row)
        table_str += "--- END | Travel Cost Between Customers"
        return table_str

    def __repr__(self):
        return self.__str__()
