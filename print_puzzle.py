
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
