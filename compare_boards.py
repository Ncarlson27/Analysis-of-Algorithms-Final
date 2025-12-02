
def compare(answer, board, n):
    differences = 0

    for row in range(0, n**2):
        for column in range(0, n**2):
            if answer[row][column] != board[row][column]:
                differences += 1

    return differences
