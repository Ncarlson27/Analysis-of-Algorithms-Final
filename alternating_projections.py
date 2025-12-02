
import numpy as np


def set_one_weight(value: int, n: int) -> list:
    """
    Params:
        value: an int representing the falue of the clue
        n: an int representing the size of the board

    Returns:
        list: a list of the weights for the clue. All 0s except the value given = 1
    """
    weights = np.zeros(n**2)
    weights[value - 1] = 1.0 # sets value to 1.0. Accounts for 0 based indexing
    return weights


def normalize(array: list) -> list:
    """
    Params:
        array: a list holding the weights of each possible value of the cell

    Returns:
        list: a list holding the weights of each possible value of the cell
            preserves needed formatting
    """
    total = np.sum(array)
    if total > 0: # makes all values sum to 1
        return array / total 
    else: # if the values are all 0, returns the array
        return array


def initialize_weights(clues: list, n: int) -> list:
    """
    Params:
        clues: n**2 x n**2 grid with 0 for blank and 1..n**2 for all clues
        n: an int representing the size of the board

    Returns:
        list: an n**2 x n**2 x n**2 weight matrix
    """
    
    weights = np.zeros((n**2, n**2, n**2)) # creates the matrix for all weights
    # basically a list for each cell

    # iterates through each cell
    for row in range(n**2): 
        for column in range(n**2):
            if clues[row][column] != 0: # if a clue
                weights[row, column] = set_one_weight(clues[row][column], n) # only one weight set
            else:
                weights[row, column] = np.ones(n**2) / n**2  # all equal weights

    return weights


def project_cells(weights: list, clues: list, n:int) -> None:
    """
    Params:
        weights: a list holding the weights of each possible value of the cell
        clues: n**2 x n**2 grid with 0 for blank and 1..n**2 for all clues
        n: an int representing the size of the board

    Returns:
        None
    """
    for row in range(n**2):
        for column in range(n**2):
            if clues[row][column] == 0:  # if not a clue
                weights[row, column] = normalize(weights[row, column])
                # normalizes the weight array for a single cell


def project_rows(weights: list, n: int) -> None:
    """
    Params:
        weights: a list holding the weights of each possible value of the cell
        n: an int representing the size of the board

    Returns:
        None
    """
    for row in range(n**2):
        for num in range(n**2):
            value = weights[row, :, num] # take specific row, all columns, specific value
            value = normalize(value)
            weights[row, :, num] = value
            # normalizes the weight array for a complete row


def project_columns(weights: list, n: int) -> None:
    """
    Params:
        weights: a list holding the weights of each possible value of the cell
        n: an int representing the size of the board

    Returns:
        None
    """
    for column in range(n**2):
        for num in range(n**2):
            value = weights[:, column, num] # take all rows, specific column, specific value
            value = normalize(value)
            weights[:, column, num] = value
            # normalizes the weight array for a complete column


def project_boxes(weights: list, n: int) -> None:
    """
    Params:
        weights: a list holding the weights of each possible value of the cell
        n: an int representing the size of the board

    Returns:
        None
    """
    # iterating over all boxes
    for box_row in range(0, n**2, n):
        for box_column in range(0, n**2, n):

            # setting specific box constraints
            rows = range(box_row, box_row + n)
            columns = range(box_column, box_column + n)

            # iterates over each value possible in a cell e.g. 1-9
            for num in range(n**2):
                values = [] # holds the weights of the values
                # iterating over a specific box
                for row in rows:
                    for column in columns:
                        # extracts the current weight for the number
                        values.append(weights[row, column, num])

                values = normalize(np.array(values))
                # normalizes the weight array for an entire box

                i = 0
                for row in rows:
                    for column in columns:
                        weights[row, column, num] = values[i]
                        # places the values back into the weights
                        i += 1


def max_change(weights: list, old_weights: list) -> float:
    """
    Params:
        weights: a list holding the current weights of each possible value of the cell
        old_weights: a list holding the old weights of each possible value of the cell

    Returns:
        float: the largest difference between the 2 weights
    """
    # finds the largest change between the last iteration's weights and the current one
    return np.max(np.abs(weights - old_weights))



def alternating_projections(clues: list, n: int, max_iters: int=500, eps: float=1e-5) -> list:
    """
    Params:
        clues: n**2 x n**2 grid with 0 for blank and 1..n**2 for all clues
        n: an int representing the size of the board
        max_iters: an int representing the amount of iterations
        eps: a float representing epsilon

    Returns:
        list: a 2-D list holding the completed Sudoku based on weights
    """
    
    # initializes all weights
    weights = initialize_weights(clues, n)

    # iterates x times = to max_iters
    for _ in range(max_iters):
        # copies the old weights to compare later
        old_weights = weights.copy()

        # projects over all 4 constraints
        project_cells(weights, clues, n)
        project_rows(weights, n)
        project_columns(weights, n)
        project_boxes(weights, n)

        # determins the largest change between weights
        change = max_change(weights, old_weights)
        

        if change < eps: # if the change is less than epsilon
            # means the algorithm is stable
            break

    # now that the weights are stable, rebuilds the sudoku 
    solution = np.zeros((n**2, n**2), dtype=int) # sets up 2-D array
    # iterates over each cell
    for row in range(n**2):
        for column in range(n**2):
            # takes the highest weight for each cell
            solution[row][column] = np.argmax(weights[row, column]) + 1

    return solution
