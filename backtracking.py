from time import time


def find_empty_cell(board: list) -> tuple|None:
    """
    Params:
        board: 2-d list representing the board

    Returns:
        Tuple: containing the position of the next empty cell
        None: if the board is filled
    """
    # just iterates through the board to find the first empty cell
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                # returns the coordinates of the empty cell
                return (i, j)
    
    # if the board is full
    return None


def is_valid(board : list, number: int, position: tuple, n: int) -> bool:
    """
    Params:
        board: 2-d list representing the board
        number: an int to check
        position: a tuple containing the position on the board
        n: an int representing the size of the board

    Returns:
        bool: True if number works in position, False if not
    
    Checks if number is valid in position
    """
    
    # checking row
    for i in range(len(board[0])):
        if board[position[0]][i] == number and i != position[1]:
            return False
    
    # checking column
    for i in range(len(board)): 
        if board[i][position[1]] == number and i != position[0]:
            return False
    

    # checking box

    # getting the coordinates of the box
    box_x = position[1] // n
    box_y = position[0] // n
    
    """
    Kind of like a 2-d list, but they're boxes
    [
    [box0, box1, box2],
    [box0, box1, box2],
    [box0, box1, box2]
    ]
    
    """
    
    # starts at where the box starts and ends where it ends
    for i in range(box_y*n, box_y*n + n): 
        for j in range(box_x*n, box_x*n + n):
            if board[i][j] == number and (i, j) != position:
                return False


    # if it passes all the checks then it's valid
    return True



def solve_sudoku(board: list, n: int) -> bool:
    """
    Params:
        board: 2-d list representing the board
        n: an int representing the size of the board

    Returns:
        bool: True if number works in position, False if not

    Recursively applies backtracking to solve the Sudoku
    """
    
    # base case
    find_empty = find_empty_cell(board) # if no empty spaces, returns None
    if find_empty is None:
        return True
    else:
        row, column = find_empty

    for i in range(1, ((n**2) + 1)): # checks all values 1-9 on 9x9 sudoku
        if is_valid(board, i, (row, column), n):
            board[row][column] = i

            if solve_sudoku(board, n):
                # recursivly checks the next empty cell
                return True
            
            # if not solved, resets the cell to 0
            board[row][column] = 0 

    # returns false if not solved yet
    return False


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



def print_board(board: list, n: int):
    """
    Params:
        board: 2-d list representing the board
        n: an int representing the size of the board

    Returns:
        nothing

    Writes the Sudoku board to a txt file in an easy to read way, shows all boxes
    """

    with open("printed_puzzle.txt", 'a') as file:
        file.write("Puzzle:\n")
        for i in range(len(board)):
            if i % n == 0 and i != 0:
                file.write("- " * ((n**2) + 1))
                file.write("\n")

            for j in range(len(board[0])):
                if j % n == 0 and j != 0:
                    file.write("|")
                
                if j == (n**2) - 1:
                    file.write(f"{board[i][j]}")
                    file.write("\n")

                else:
                    file.write(f"{board[i][j]} ")
        
        file.write("\n\n")


def main():
    """
    Params:
        none

    Returns:
        nothing

    Calls read_file() to obtain sudoku board
    Prints the board
    Calls solve_sudoku() 
    Prints solved board and the time taken
    """
    board = read_file("basic_sudoku.txt")
    n = 3

    print_board(board, n)
   
    start = time()
    solve_sudoku(board, n)
    end = time()

    print_board(board, n)
    print(f"Sudoku solved in: {end-start}")


    """
    board = read_file("sixteen.txt")
    n = 4

    print_board(board, n)
   
    start = time()
    solve_sudoku(board, n)
    end = time()

    print_board(board, n)
    print(f"Sudoku solved in: {end-start}")
    """
    




if __name__ == "__main__":
    main()
