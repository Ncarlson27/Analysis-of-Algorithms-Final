from time import time
from print_puzzle import print_board
from backtracking import backtrack
from simulated_annealing import simulated_annealing
from alternating_projections import alternating_projections
from compare_boards import compare


def read_file(file_name):

    board = []
    
    with open(file_name, 'r') as file:
        for line in file.readlines():
            temp = []
            line = line.strip().split()
            
            for num in line:
                temp.append(int(num))
            
            board.append(temp)
    
    return board

def main():
    """
    Params:
        none

    Returns:
        nothing

    Calls read_file() to obtain sudoku board
    Prints the board
    Calls backtrack() 
    Prints solved board and the time taken
    """
    n = 3
   
    board = read_file("basic_sudoku.txt")
    print_board(board, n)
    
    # backtracking
    start = time()
    backtrack(board, n)
    end = time()

    print_board(board, n)
    print(f"Sudoku solved through backtracking in: {end-start}")



    # alternating projections
    board = read_file("basic_sudoku.txt")
    
    start = time()
    alt = alternating_projections(board, n)
    end = time()

    print_board(alt, n)
    print(f"Alternating projections completed in: {end-start}")

    
    # simmulating annealing
    board = read_file("basic_sudoku.txt")

    start = time()
    board, conflicts = simulated_annealing(board, n)
    end = time()

    print(f"Alternating projections completed in: {end-start}\nConflicts: {conflicts}")
    print_board(board, n)



if __name__ == "__main__":
    main()
