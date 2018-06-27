from random import randint, shuffle


def mutation_slice_points(chromosome_len: int) -> (int, int):
    slice_point_1 = randint(0, chromosome_len - 3)
    slice_point_2 = randint(slice_point_1 + 2, chromosome_len - 1)
    return slice_point_1, slice_point_2


def mutation_inversion(chromosome: list) -> list:
    slice_point_1, slice_point_2 = mutation_slice_points(len(chromosome))

    return chromosome[:slice_point_1] + list(reversed(chromosome[slice_point_1:slice_point_2])) + chromosome[slice_point_2:]


def mutation_scramble(chromosome: list) -> list:
    slice_point_1, slice_point_2 = mutation_slice_points(len(chromosome))
    scrambled = chromosome[slice_point_1:slice_point_2]
    shuffle(scrambled)

    return chromosome[:slice_point_1] + scrambled + chromosome[slice_point_2:]
