import ga_params
import utils
from nodes import Customer as Node
from typing import List

List_Node = List[Node]


class Chromosome:
    route = []                  # type: list
    value = None                # type: float

    vehicles_count = None       # type: int
    vehicles_routes = None      # type: list
    route_rounds = None         # type: int
    total_travel_dist = None    # type: float
    total_elapsed_time = None   # type: float
    # deport is 0
    current_load = None         # type: int
    elapsed_time = None         # type: float
    max_elapsed_time = None     # type: float
    distance_table = None       # type: list

    higher_value_fitter = False

    def __init__(self, route: iter):
        self.route = list(route)
        self.value = self.get_cost_score()

    def initial_port(self):
        self.vehicles_count = 1
        self.vehicles_routes = [[0]]
        self.route_rounds = 0
        self.total_travel_dist = 0
        self.total_elapsed_time = 0
        self.current_load = 0
        self.elapsed_time = 0
        self.max_elapsed_time = 0

    @staticmethod
    def get_distance(source: int, dest: int) -> float:
        # must be overwritten
        pass

    @staticmethod
    def get_node(index: int) -> Node:
        # must be overwritten
        pass

    @staticmethod
    def get_travel_time(distance: float) -> float:
        return distance / ga_params.vehicle_speed_avg

    @staticmethod
    def get_travel_cost(distance: float) -> float:
        return distance * ga_params.vehicle_cost_per_dist

    def check_time_and_go(self, source: int, dest: int, distance: float=None) -> bool:
        if distance is None:
            distance = self.get_distance(source, dest)
        dest_customer = self.get_node(dest)  # type: Node
        elapsed_new = self.get_travel_time(distance) + self.elapsed_time
        if elapsed_new <= dest_customer.due_time:
            return_time = self.get_travel_time(self.get_distance(dest, 0))
            deport_due_time = self.get_node(0).due_time
            if elapsed_new + dest_customer.service_time + return_time <= deport_due_time:
                self.move_vehicle(source, dest, distance=distance)
                return True
            else:
                return False
        else:
            return False

    def check_capacity(self, dest: int) -> bool:
        dest_customer = self.get_node(dest)  # type: Node
        return self.current_load + dest_customer.demand <= ga_params.vehicle_capacity

    @staticmethod
    def get_vehicle_count_preference_cost(vehicles_count: int, deport_working_hours: int) -> float:
        # less_vehicles_preference * (vehicles_count) + less_deport_working_hours * (deport_working_hours)
        # vehicles_count_over_deport_hours_preference = less_vehicles_preference / less_deport_working_hours
        return ga_params.vehicles_count_over_deport_hours_preference * vehicles_count + deport_working_hours

    def move_vehicle(self, source: int, dest: int, distance: float=None):
        if distance is None:
            distance = self.get_distance(source, dest)
        self.total_travel_dist += distance
        self.elapsed_time += self.get_travel_time(distance)
        self.max_elapsed_time = max(self.elapsed_time, self.max_elapsed_time)
        self.vehicles_routes[-1].append(dest)
        if dest == 0:
            self.route_rounds += 1
            self.current_load = 0
        else:
            dest_customer = self.get_node(dest)  # type: Node
            self.current_load += dest_customer.demand

    def add_vehicle(self):
        self.vehicles_count += 1
        self.vehicles_routes.append([0])
        self.elapsed_time = 0
        self.current_load = 0

    def get_cost_score(self) -> float:
        # demand ~ capacity
        # time ~ due_time
        self.initial_port()

        for source, dest in utils.pairwise([0] + self.route + [0]):
            if self.check_capacity(dest):
                # current vehicle has the capacity to go from source to dest
                if not self.check_time_and_go(source, dest):
                    # current vehicle hasn't enough time to go to dest -> new vehicle
                    # current vehicle should go back from source to deport
                    self.move_vehicle(source, 0)
                    # current_load = 0
                    # new vehicle starts from deport heading dest
                    self.add_vehicle()
                    self.move_vehicle(0, dest)
            else:
                # current vehicle hasn't the capacity to go to dest
                # current vehicle should go back from source to deport
                self.move_vehicle(source, 0)
                # head from deport to dest
                distance = self.get_distance(0, dest)  # just for speeding up (caching)
                if not self.check_time_and_go(0, dest, distance):
                    # too late to go from deport to dest on current vehicle -> new vehicle
                    self.add_vehicle()
                    self.move_vehicle(0, dest, distance)

        total_travel_cost = Chromosome.get_travel_cost(self.total_travel_dist)
        total_vehicles_and_deport_working_hours_cost = self.get_vehicle_count_preference_cost(
            vehicles_count=self.vehicles_count,
            deport_working_hours=self.max_elapsed_time)
        return total_travel_cost + total_vehicles_and_deport_working_hours_cost

    def plot_get_route_cords(self) -> list:
        rounds = []
        for vehicle_route in self.vehicles_routes:
            route_x_holder = []
            route_y_holder = []
            for customer_index in vehicle_route:
                customer = self.get_node(customer_index)    # type: Node
                route_x_holder.append(customer.x)
                route_y_holder.append(customer.y)
            rounds.append((route_x_holder, route_y_holder))
        return rounds

    def __iter__(self):
        for r in self.route:
            yield r

    def __lt__(self, other):
        return self.value < other.value

    def __eq__(self, other):
        return self.value == other.value

    def __radd__(self, other):
        return self.value + other

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.route) + ", value= " + str(self.value) + ", vehicles_count= " + str(self.vehicles_count) \
               + ", total deport visits=" + str(self.route_rounds) \
               + ", deport working hours=" + str(self.max_elapsed_time) + ", routes= " + str(self.vehicles_routes)

    def __repr__(self):
        return self.__str__()
