from utilities import *
from methods import *


def reduce_puzzle(grid):
    """
    Apply all method in an attempt to reduce every box of the sudoku
    to one element
    Args:
       grid(dict) - Current state of the sudoku

    Returns: Upon completion, ie no change between iteration
       vlaues(dict) - Current state of the sudoku
    """
    stuck = False
    while not stuck:

        begin = len([i for i in boxes if len(grid[i]) == 1])

        grid = eliminate(grid)
        grid = only_choice(grid)
        grid = naked_twins(grid)
        #grid = naked_triple(grid) - something for the future
        end = len([i for i in boxes if len(grid[i]) == 1])
        stuck = begin == end

        sanity = len([i for i in boxes if len(grid[i]) == 0])
        if sanity > 0:
            return

    return grid


def search(grid):
    """
    Search all possible values after applying reduce_puzzle
    :param grid: Sudoku grid
    :return: Solved Sudoku
    """
    grid = reduce_puzzle(grid)
    if not grid:
        return False

    if all(len(grid[v]) == 1 for v in boxes):
        return grid

    num, idx = min((len(grid[s]), s) for s in boxes if len(grid[s]) > 1)
    for i in grid[idx]:
        temp_sudoku = grid.copy()
        temp_sudoku[idx] = i
        solving = search(temp_sudoku)
        if solving:
            return solving


def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    grid = make_grid(grid)
    return search(grid)


def test_solution(grid):
    """
    verify the solution found satisfies the rules of a Sudoku
    :param grid: A possible completed Sudoku
    :return (boolean): True if all rules satisfied else False
    """
    test_sum = 0
    for unit in all_units:
        test_sum += sum([int(grid[s]) for s in unit]) == 45
    return test_sum == len(all_units)

if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    #diag_sudoku_grid = '..5..7..2.7..4..9.1..9..8..8..2..7...2..5..8...7..6..5..2..4..9.1..7..3.7..3..6..'
    
    assert len(diag_sudoku_grid) == 81

    solution = solve(diag_sudoku_grid)
    display(solution)
    assert test_solution(solution)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue')
