import numpy as np


def fill_remaining(chromosome: list, filling: list) -> list:
    fill_index = 0
    for ch_index, ch_bit in enumerate(chromosome):
        if ch_bit is None:
            while filling[fill_index] in chromosome:
                # if filling[fill_index] == 0:
                #     if not any(x == 0 and x is not None for x in chromosome):
                #         break
                fill_index += 1
            chromosome[ch_index] = filling[fill_index]

    return chromosome


def crossover_uox(parent1: list, parent2: list) -> (list, list):
    if len(parent1) != len(parent2):
        raise Exception("Crossover error: Parents length are not equal")
    chrome_len = len(parent1)
    mask_binary = np.random.randint(2, size=chrome_len)
    # mask_binary = [0, 1, 1, 0, 1, 1]
    child1 = []
    child2 = []

    for index, mask in enumerate(mask_binary):
        if mask:
            child1.append(parent1[index])
            child2.append(parent2[index])
        else:
            child1.append(None)
            child2.append(None)

    child1 = fill_remaining(child1, parent2)
    child2 = fill_remaining(child2, parent1)

    return child1, child2
