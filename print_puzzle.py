def print_board(board: list, n: int = 3, file_name = None):
    """
    Params:
        board: 2-d list representing the board
        n: an int representing the size of the board
        file_name: a string holding the file name

    Returns:
        nothing

    Writes the Sudoku board to a txt file (if file name is given) in an easy to read way, shows all boxes
    If no file name given, prints to the terminal
    """
    if file_name is not None:
        with open(file_name, 'a') as file:
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

    else:
        print("Puzzle:\n")
        for i in range(len(board)):
            if i % n == 0 and i != 0:
                print("- " * ((n**2) + 1))

            for j in range(len(board[0])):
                if j % n == 0 and j != 0:
                    print("|", end="")
                
                if j == (n**2) - 1:
                    print(f"{board[i][j]}")

                else:
                    print(f"{board[i][j]} ", end="")