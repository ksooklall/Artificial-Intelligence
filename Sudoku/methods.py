from utilities import *


def naked_twins(grid):
    """Eliminate grid using the naked twins strategy.
    Args:
        grid(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        grid with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    possible_twins = [i for i in boxes if len(grid[i]) == 2]
    twins = [(t, j) for t in possible_twins for j in possible_twins if t != j and grid[t] == grid[j]]

    # Eliminate the naked twins as possibilities for their peers
    for unit in all_units[:-2]:
        for twin in twins:
            if twin[0] in unit and twin[1] in unit: #Verify that the twin is in the unit
                for u in unit:
                    if u != twin[0] and u != twin[1]:
                        if len(grid[twin[0]]) == 2: # Verify that this twin wasn't already taken care of
                            grid = assign_value(grid, u, grid[u].replace(grid[twin[0]][0], ''))
                            grid = assign_value(grid, u, grid[u].replace(grid[twin[0]][1], ''))
    return grid


def only_choice(grid):
    """
    There may be only one possible choice for a particular unit
    Args:
        grid(dict) - Current state of the sduoku
                       Key: Box index, V: Current value in that box
    Returns:
        grid(dict) - New state
    """
    for unit in all_units:
        for d in '123456789':
            choices = [n for n in unit if d in grid[n]]
            if len(choices) == 1:
                grid = assign_value(grid, choices[0], d)
    return grid


def eliminate(grid):
    """
    Eliminate grid from current pool with the given grid
    Args:
        grid(dict) - Current state of the sduoku
                       Key: Box index, V: Current value in that box
    Returns:
        grid(dict) - New state
    """
    given = [k for k in grid.keys() if len(grid[k]) == 1]
    for i in given:
        curr_val = grid[i]
        for jj in peers[i]:
            grid = assign_value(grid, jj, grid[jj].replace(curr_val, ''))

    return grid
