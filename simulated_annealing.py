import math
from copy import deepcopy
from random import shuffle, randint, sample, random


def fill_missing(board: list, n: int) -> list:
    """
    Params:
        board: 2-d list representing the board
        n: an int representing the size of the board

    Returns:
        list: returns a 2-d list with a randomly filled board 
    """
    # makes a deep copy fo the board to not modify the original
    board_state = deepcopy(board) 

    # iterating across each box
    for box_row in range(0, n**2, n): # boxes are size n by n
        for box_column in range(0, n**2, n):

            current_values = set() # holds current values i.e. clues
            empty_cells = [] # holds starting empty cells

            # iterates through each box
            for row in range(box_row, box_row + n): 
                for column in range(box_column, box_column + n):
                    # if the value is not already filled i.e. a clue
                    if board[row][column] != 0:
                        current_values.add(board[row][column])
                    else:
                        empty_cells.append((row, column))

            
            # gets the vaues 1 - n**2 to be used to fill the box
            # ignores the clues in the box 
            missing = list(set(range(1, (n**2)+1)) - current_values)
            shuffle(missing) # shuffles the usable numbers


            # iterates through the list of empty cells and missing values
            # fills the empty cell with a random value
            for (row, column), digit in zip(empty_cells, missing):
                board_state[row][column] = digit

    return board_state


def calculate_cost(board_state: list, n: int) -> int:
    """
    Params:
        board_state: 2-d list representing the current board state
        n: an int representing the size of the board

    Returns:
        int: returns the number of conflicts in the board
    """
    # the amount of conflicts
    conflicts = 0

    for r in range(n**2):
        row = board_state[r] # gets the list representing each row
        conflicts += n**2 - len(set(row)) # converts to set, so duplicates are removed
        # compares the total amount of possible conflicts (n**2) to the size

    
    for c in range(n**2):
        column = [board_state[r][c] for r in range(n**2)] # gets the list of eah column
        conflicts += n**2 - len(set(column)) # converts to set, so duplicates are removed
        # compares the total amount of possible conflicts (n**2) to the size

    return conflicts


def swap_random_values(board_state: list, clues: set, n: int) -> list:
    """
    Params:
        board: 2-d list representing the board
        clues: a set containing tuple coordinates of the clues 
        n: an int representing the size of the board

    Returns:
        list: returns a 2-d list after swapping values 
    """
    # makes a deep copy fo the board to not modify the original
    new_board = deepcopy(board_state)

    # generating a random box
    # boxes start in increments of n e.g. 0, 3, 6 for n = 3
    box_row = n * randint(0, n-1)
    box_column = n * randint(0, n-1)

    # keeps track of free to change cells, i.e. non-clue cells
    free = [] 

    # finds all free cells
    for row in range(box_row, box_row + n):
        for column in range(box_column, box_column + n):
            if (row, column) not in clues:
                free.append((row, column))

    # if there's fewer than 2 free cells
    if len(free) < 2:
        return new_board 

    # randomly swaps 2 values in the box
    (r1, c1), (r2, c2) = sample(free, 2)
    new_board[r1][c1], new_board[r2][c2] = new_board[r2][c2], new_board[r1][c1]

    return new_board



def simulated_annealing(board: list, n: int) -> list|int:
    """
    Params:
        board: 2-d list representing the board
        n: an int representing the size of the board

    Returns:
        list: returns a 2-d list of the final board state
        int: returns the number of conflicts
    """
    
    # keeps track of all the positions of the clues
    clues = {(row, column) for row in range(n**2) for 
             column in range(n**2) if board[row][column] != 0}

    # creates initial randomly generated board state
    state = fill_missing(board, n)
    # finds the current cost
    current_cost = calculate_cost(state, n) # current conflicts

   
    T = 1.0 # starting temp
    T_min = 1e-6 # minimum temp
    alpha = 0.995 # how fast it cools
    iterations_per_temp = 1000 # iterations per temp value

    while T > T_min: 
        for _ in range(iterations_per_temp): # iterate 1000 times before it cools
            # swaps a value, calculates the cost, and gets the change between them 
            swaped_board = swap_random_values(state, clues, n) 
            new_cost = calculate_cost(swaped_board, n)
            delta = new_cost - current_cost

            if delta <= 0:
                # accepts better state
                state = swaped_board
                current_cost = new_cost
            else:
                # accepts worse state with a given propability 
                p = math.exp(-delta / T)
                if random() < p:
                    state = swaped_board
                    current_cost = new_cost

            if current_cost == 0: # return if no conflicts
                return state  

        # cool the temperature and go again
        T *= alpha

    # if there are still conflicts once cooled
    return state