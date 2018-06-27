from random import shuffle


def selection_tournament_deterministic(population: list, selection_size: int, k: int=2, repeat: bool=False, 
                                       reverse: bool=False) -> list:
    pop_copy = list(population)
    selected = []
    for selection_index in range(selection_size):
        shuffle(pop_copy)
        tournament = pop_copy[:k]
        if reverse:
            selected_in_tournament = min(tournament)
        else:
            selected_in_tournament = max(tournament)
        if not repeat:
            pop_copy.remove(selected_in_tournament)
        selected.append(selected_in_tournament)

    return selected
