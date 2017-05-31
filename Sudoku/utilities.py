assignments = []


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [i + j for i in A for j in B]


diag = False

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)
row_units = [cross(i, cols) for i in rows]
col_units = [cross(rows, i) for i in cols]
square_units = [cross(r, c) for r in ['ABC', 'DEF', 'GHI'] for c in ['123', '456', '789']]
diagonal_unit = [[r + c for r, c in zip(rows, cols)], [r + c for r, c in zip(rows, cols[::-1])]]

if diag:
    all_units = row_units + col_units + square_units + diagonal_unit
else:
    all_units = row_units + col_units + square_units

units = dict((i, [s for s in all_units if i in s]) for i in boxes)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in boxes)


def assign_value(values, box, value):
    """
    Assigns a value to a given box. If it updates the board record it.
    Args:
       values(dict): Current state of the sudoku board
       box(str): A location on the board, key of values
       value(str): An updated value that will be placed in the box

    Returns:
        Values
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return


def make_grid(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """

    digits = '123456789'
    s_grid = dict(zip(boxes, grid))
    for k, v in s_grid.items():
        if v == '.':
            s_grid[k] = digits
    return s_grid