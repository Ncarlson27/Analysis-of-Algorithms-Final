
from time import time
from print_puzzle import print_board
from backtracking import backtrack
from simulated_annealing import simulated_annealing

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

    
    board = read_file("basic_sudoku.txt")
    n = 3
    
    print_board(board, n)
    
    start = time()
    backtrack(board, n)
    end = time()

    print_board(board, n)
    print(f"Sudoku solved through backtracking in: {end-start}")
    
    
    board = read_file("basic_sudoku.txt")
    start = time()
    board, conflicts = simulated_annealing(board, n)
    end = time()

    if conflicts == 0:
        print("Solved:")
        print(f"Sudoku solved through simulated annealing in: {end-start}")
        print_board(board, n)
    else:
        print("No solution found through simulated annealing")
        print(f"Took: {end-start}\nConflicts: {conflicts}")
        print_board(board, n)




if __name__ == "__main__":
    main()
