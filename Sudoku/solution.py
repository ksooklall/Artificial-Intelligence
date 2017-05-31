assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [i+j for i in A for j in B]

diag = True
                                                     
rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)
row_units = [cross(i, cols) for i in rows]
col_units = [cross(rows, i) for i in cols]
square_units = [cross(r, c) for r in ['ABC', 'DEF', 'GHI'] for c in ['123', '456', '789']]
diagonal_unit = [[r+c for r,c in zip(rows,cols)], [r+c for r,c in zip(rows, cols[::-1])]]

if diag:
    all_units = row_units + col_units + square_units + diagonal_unit
else:
    all_units = row_units + col_units + square_units                                            

units = dict((i, [s for s in all_units if i in s]) for i in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)

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

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        Values with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    possible_twins = [i for i in boxes if len(values[i]) == 2]
    twins = [(t, j) for t in possible_twins for j in possible_twins if t != j and values[t] == values[j]]

    # Eliminate the naked twins as possibilities for their peers
    for unit in all_units[:-2]:
        for twin in twins:
            if twin[0] in unit and twin[1] in unit: #Verify that the twin is in the unit
                for u in unit:
                    if u != twin[0] and u != twin[1]:
                        if len(values[twin[0]]) == 2: # Verify that this twin wasn't already taken care of
                            values = assign_value(values, u, values[u].replace(values[twin[0]][0], ''))
                            values = assign_value(values, u, values[u].replace(values[twin[0]][1], ''))
    return values

def grid_values(grid):
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

def eliminate(values):
    """
    Eliminate values from current pool with the given values
    Args:
        values(dict) - Current state of the sduoku
                       Key: Box index, V: Current value in that box
    Returns:
        values(dict) - New state
    """
    given = [k for k in values.keys() if len(values[k]) == 1]
    for i in given:
        curr_val = values[i]
        for j in peers[i]:
            values = assign_value(values, j, values[j].replace(curr_val, ''))
    return values

def only_choice(values):
    """
    There may be only one possible choice for a particular unit
    Args:
        values(dict) - Current state of the sduoku
                       Key: Box index, V: Current value in that box
    Returns:
        values(dict) - New state        
    """
    for unit in all_units:
        for d in '123456789':
            choices = [n for n in unit if d in values[n]]
            if len(choices) == 1:
                values = assign_value(values, choices[0], d)
    return values

def reduce_puzzle(values):
    """
    Apply all method in an attempt to reduce every box of the sudoku
    to one element
    Args:
       values(dict) - Current state of the sudoku

    Returns: Upon completion, ie no change between iteration
       vlaues(dict) - Current state of the sudoku
    """
    stuck = False
    while not stuck:

        begin = len([i for i in boxes if len(values[i]) == 1])

        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        #values = naked_triple(values) - something for the future
        end = len([i for i in boxes if len(values[i]) == 1])
        stuck = begin == end
        
        sanity = len([i for i in boxes if len(values[i]) == 0])
        if sanity > 0:
            return


    return values

def search(values):
    values = reduce_puzzle(values)

    if not values:
        return False

    #if all(len(v) == 1 for k, v in values.items()):
    if all(len(values[v]) == 1 for v in boxes):
        return values

    num, idx = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    for i in values[idx]:
        temp_sudoku = values.copy()
        temp_sudoku[idx] = i
        solving = search(temp_sudoku)
        if solving:
            return solving

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)

def test_solution(values):
    test_sum = 0
    for unit in all_units:
        test_sum += sum([int(values[s]) for s in unit]) == 45
    return test_sum == len(all_units)

if __name__ == '__main__':
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    
    assert len(diag_sudoku_grid) == 81

    solution = solve(diag_sudoku_grid)
    assert test_solution(solution)
    display(solution)

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
