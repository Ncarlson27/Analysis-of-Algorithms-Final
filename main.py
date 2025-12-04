from time import time
from print_puzzle import print_board
from backtracking import backtrack
from simulated_annealing import simulated_annealing
from alternating_projections import alternating_projections
from mrv_method import mrv_solve, get_sets
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


def test(n, method, file_name):

    for i in range(3):
        match i:
            case 0:
                with open(file_name, 'a') as file:
                    file.write(f"\n\n\n----------Easy file----------\n\n")
            case 1:
                with open(file_name, 'a') as file:
                    file.write(f"\n\n\n----------Medium file----------\n\n")
            case 2:
                with open(file_name, 'a') as file:
                    file.write(f"\n\n\----------Hard file----------\n\n")
        for j in range(5):
            match i:
                case 0:
                    board = read_file("easy_sudoku.txt")
                    answer = read_file("easy_sudoku_answer.txt")
                case 1:
                    board = read_file("medium_sudoku.txt")
                    answer = read_file("medium_sudoku_answer.txt")
                case 2:
                    board = read_file("hard_sudoku.txt")
                    answer = read_file("hard_sudoku_answer.txt")
                
            with open(file_name, 'a') as file:
                file.write(f"---Test {j+1}---\n\n")
                
            times = []


            if method == "backtracking":
                start = time()
                backtrack(board, n)
                end = time()
                times.append(end-start)
            elif method == "mrv method":
                rows, columns, boxes = get_sets(board, n)
                start = time()
                mrv_solve(board, n, rows, columns, boxes)
                end = time()
                times.append(end-start)
            elif method == "alternating projection":
                start = time()
                board = alternating_projections(board, n)
                end = time()
                times.append(end-start)
            elif method == "simulated annealing":
                start = time()
                board = simulated_annealing(board, n)
                end = time()
                times.append(end-start)


            differences = []
            differences.append(compare(board, answer, n))

            with open(file_name, 'a') as file:
                file.write(f"Puzzle completed with {method}\nTime taken: {times[-1]}\n" \
                           f"Differences: {differences[-1]}\n")
                
                file.write("End board:\n")

            print_board(board, n, file_name)
        
        with open(file_name, 'a') as file:
                file.write(f"Average completion time: {sum(times)//len(times)}\n")
                file.write(f"Average differences: {sum(differences)//len(differences)}\n")



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

    file_name = "test_results_backtracking.txt"
    with open(file_name, 'w') as file:
        file.write("")
    test(n, "backtracking", file_name)

    file_name = "test_results_mrv.txt"
    with open(file_name, 'w') as file:
        file.write("")
    
    test(n, "mrv method", file_name)

    print('Done')

    """
    file_name = "test_results_alternating.txt"
    with open(file_name, 'w') as file:
        file.write("")
    test(n, "alternating projection", file_name)

    file_name = "test_results_annealing.txt"
    with open(file_name, 'w') as file:
        file.write("")
    test(n, "simulated annealing", file_name)
    """


    n = 4
    board = read_file("16.txt")
    answer = read_file("16_answer.txt")

    rows, columns, boxes = get_sets(board, n)
    start = time()
    mrv_solve(board, n, rows, columns, boxes)
    end = time()

    
    
    print(f"Sudoku completed in: {end-start}")
    print_board(board)
    


if __name__ == "__main__":
    main()
