
def get_mrv_cell(board, rows, columns, boxes, n):
    best_cell = None
    best_options = None

    for row in range(n**2):
        for column in range(n**2):
            if board[row][column] == 0:  # empty cell
                box_x, box_y = row // n, column // n

                # compute legal values for this cell
                used = rows[row] | columns[column] | boxes[box_x][box_y]
                options = [value for value in range(1, n**2 + 1) if value not in used]

                if best_options is None or len(options) < len(best_options):
                    best_options = options
                    best_cell = (row, column)

                # MRV early exit: only 1 option = best possible
                if len(best_options) == 1:
                    return best_cell, best_options

    return best_cell, best_options

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
        for box_column in range(0, n**2, n):

            # setting specific box constraints
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
  


def mrv_solve(board: list, n:int, rows, columns, boxes) -> list:

    position, options = get_mrv_cell(board, rows, columns, boxes, n)

    if position is None:
        return board  # solved

    row_value, column_value = position
    box_x_value = row_value // n
    box_y_value = column_value // n

    for value in options:
        board[row_value][column_value] = value
        rows[row_value].add(value)
        columns[column_value].add(value)
        boxes[box_x_value][box_y_value].add(value)

        if mrv_solve(board, n, rows, columns, boxes):
            return True
        
        board[row_value][column_value] = 0
        rows[row_value].discard(value)
        columns[column_value].discard(value)
        boxes[box_x_value][box_y_value].discard(value)

    return False

