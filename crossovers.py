import numpy as np


def fill_remaining(chromosome: list, filling: list) -> list:
    fill_index = 0
    for ch_index, ch_bit in enumerate(chromosome):
        if ch_bit is None:
            while filling[fill_index] in chromosome:
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


def crossover_cx(parent1: list, parent2: list) -> (list, list):
    length = len(parent1)
    if length != len(parent2):
        raise Exception("Crossover error: Parents length are not equal")

    p1 = {}
    p2 = {}
    p1_inv = {}
    p2_inv = {}
    for i in range(length):
        p1[i] = parent1[i]
        p1_inv[p1[i]] = i
        p2[i] = parent2[i]
        p2_inv[p2[i]] = i

    cycles_indices = []
    while p1 != {}:
        i = min(list(p1.keys()))
        cycle = [i]
        start = p1[i]
        check = p2[i]
        del p1[i]
        del p2[i]

        while check != start:
            i = p1_inv[check]
            cycle.append(i)
            check = p2[i]
            del p1[i]
            del p2[i]

        cycles_indices.append(cycle)

    child = ({}, {})

    for run, indices in enumerate(cycles_indices):
        first = run % 2
        second = (first + 1) % 2

        for i in indices:
            child[first][i] = parent1[i]
            child[second][i] = parent2[i]

    child1 = []
    child2 = []
    for i in range(length):
        child1.append(child[0][i])
        child2.append(child[1][i])

    return child1, child2

    # child1, child2 = crossover_cx([8, 4, 7, 3, 6, 2, 5, 1, 9, 0], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    # print(child1)   # 8 1 2 3 4 5 6 7 9 0
    # print(child2)   # 0 4 7 3 6 2 5 1 8 9


def crossover_pmx(parent1: list, parent2: list) -> (list, list):
    if len(parent1) != len(parent2):
        raise Exception("Crossover error: Parents length are not equal")
    chrome_len = len(parent1)
    p1_inv = {}
    p2_inv = {}
    child1 = list(parent1)
    child2 = list(parent2)

    for i in range(chrome_len):
        p1_inv[parent1[i]] = i
        p2_inv[parent2[i]] = i

    # crossover points random from 0 to chrome_len
    cx_point1 = np.random.randint(0, chrome_len)
    cx_point2 = np.random.randint(0, chrome_len - 1)

    # prepare it for loop from point1 to point2
    if cx_point2 >= cx_point1:
        cx_point2 += 1
    else:
        cx_point1, cx_point2 = cx_point2, cx_point1

    # Loop between crossover points
    for i in range(cx_point1, cx_point2):
        # Selected values before changing the parent
        check1 = child1[i]
        check2 = child2[i]
        # Swap matched !
        parent1[i], parent1[p1_inv[check2]] = check2, check1
        parent2[i], parent2[p2_inv[check1]] = check1, check2

        p1_inv[check1] = p1_inv[check2]
        p1_inv[check2] = p1_inv[check1]
        p2_inv[check1] = p2_inv[check2]
        p2_inv[check2] = p2_inv[check1]

    return child1, child2

    # p1, p2 = list(range(1, 101)), list(range(1, 101))
    #
    # # child1, child2 = crossover_pmx([8, 4, 7, 3, 6, 2, 5, 1, 9], [1, 2, 3, 4, 5, 6, 7, 8, 9])
    # child1, child2 = crossover_pmx(p1, p2)
    # print(child1)
    # print(child2)
