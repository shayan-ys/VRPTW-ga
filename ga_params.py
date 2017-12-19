from crossovers import crossover_uox, crossover_cx, crossover_pmx
from selections import selection_tournament_deterministic
from mutations import mutation_inversion, mutation_scramble

print_benchmarks = True
draw_plot = False
export_spreadsheet = True

MAX_GEN = 60000

vehicle_cost_per_dist = 1.0
vehicle_speed_avg = 1.0
vehicle_capacity = 200
vehicles_count_over_deport_hours_preference = 1000

run_file = {
    'name': 'C101_200',
    'header_map': {
        'XCOORD': 'x_coordinates',
        'YCOORD': 'y_coordinates',
        'DEMAND': 'demand',
        'READY_TIME': 'ready_time',
        'DUE_DATE': 'due_time',
        'SERVICE_TIME': 'service_time',
    }
}

population = {
    'pop_size': 100,
    'crossover_method': staticmethod(crossover_pmx),
    'mutation_method': staticmethod(mutation_inversion),
    'removing_method': staticmethod(selection_tournament_deterministic),
    'selection_method': staticmethod(selection_tournament_deterministic),
    'selection_pressure': 2,  # tournament size (k)
    'selection_repeat': False,
    'parent_selection_ratio': 0.8,
    'mutation_ratio': 0.1,
    'elitism_count': 5,
    # plot
    'plot_x_div': 100,
    'plot_x_window': 100
}
