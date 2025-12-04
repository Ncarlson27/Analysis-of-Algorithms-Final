
from random import shuffle 
from copy import deepcopy 
from print_puzzle import print_board 
from main import read_file 
from time import time 
from compare_boards import compare 
# idea: # figure out how many of each value is left after the clues 
# # then create a pool, randomly (maybe) distribute them 
# # have sets or something else to easily tell if the value is already 
# in that row, column, or box 


def find_empty_cell(board: list) -> tuple|None: 
    """ Params: board: 2-d list representing the board 
    Returns: Tuple: containing the position of the next empty cell None: if the board is filled """ 
    # just iterates through the board to find the first empty cell 
    for i in range(len(board)): 
        for j in range(len(board[0])): 
            if board[i][j] == 0: 
                # returns the coordinates of the empty cell 
                return (i, j) 
    
    # if the board is full 
    return None 

def get_pool(board: list, n:int) -> list: 
    pool = [] 
    for i in range(1, (n**2) + 1): 
        for j in range(n**2): 
            pool.append(i)

    for i in range(n**2): 
        for j in range(n**2): 
            if board[i][j] != 0: 
                pool.remove(board[i][j]) 
    
    return pool 
            
def get_sets(board: list, n: int) -> list: 
    rows = [] 
    columns = [] 
    boxes = [] # will be a 2-D list of sets 
    # mimics the sudoku box set up 
     
    # getting rows
    for row in board: 
        rows.append(set(row)) 
        rows[-1].discard(0)
    
    # getting columns 
    for i in range(n**2): 
        column = [] 
        for j in range(n**2): 
            column.append(board[j][i])

        columns.append(set(column)) 
        columns[-1].discard(0) 
            
    # getting boxes 
    for box_row in range(0, n**2, n): # iterating over each box 
        box = [] 
        for box_column in range(0, n**2, n): # setting specific box constraints 
            row_range = range(box_row, box_row + n) 
            column_range = range(box_column, box_column + n) 
            
            
            temp_box = [] # holds the contents of the boxes 
            # iterates over every value in the box 
            for i in row_range: 
                for j in column_range: 
                    # adds the number to the list 
                    temp_box.append(board[i][j]) 
            temp_box = set(temp_box) 
            temp_box.discard(0) 
            box.append(temp_box) 
        
        boxes.append(box) 
    
    
    return rows, columns, boxes 
                

def pool_solve(board: list, n:int, max_iters=1000) -> list: 
    pool = get_pool(board, n) 
    rows, columns, boxes = get_sets(board, n) 
    
    for _ in range(max_iters): 
        shuffle(pool) 
        pool_state = deepcopy(pool) 
        board_state = deepcopy(board) 
        rows_state = deepcopy(rows) 
        columns_state = deepcopy(columns) 
        boxes_state = deepcopy(boxes) 
    
        done = False 
        while not done: 
            position = find_empty_cell(board_state) # tuple containing (i, j) position 
            if position is None: # if all cells are filled, board is solved 
                return board_state 
        
            row_value, column_value = position 
            box_x_value = row_value // n 
            box_y_value = column_value // n 
            
            for value in pool_state: 
                if board_state[row_value][column_value] == 0 \
                and value not in rows_state[row_value] and value not in columns_state[column_value] \
                and value not in boxes_state[box_x_value][box_y_value]: 
                    
                    board_state[row_value][column_value] = value 
                    
                    pool_state.remove(value) 
                    rows_state[row_value].add(value) 
                    columns_state[column_value].add(value) 
                    boxes_state[box_x_value][box_y_value].add(value)
                    break 
            
            if find_empty_cell(board_state) is None: 
                done = True 
            elif board_state[row_value][column_value] == 0: 
                board_state[row_value][column_value] = -1 
                    
    return board_state 


if __name__ == "__main__": 
    n = 3 
    board = read_file("easy_sudoku.txt") 
    answer = read_file("easy_sudoku_answer.txt") 

    start = time() 
    board = pool_solve(board, n) 
    end = time() 
    
    print(f"Errors: {compare(answer, board, n)}") 
    print(f"Time: {end-start}") 
    print_board(board)