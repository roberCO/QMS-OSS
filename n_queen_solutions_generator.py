# This code is contributed by Nikhil Vinay
# This code was extracted from https://www.geeksforgeeks.org/printing-solutions-n-queen-problem/

# Python program for above approach
import math

result = []

# Program to solve N-Queens Problem
def solveBoard(board, row, rowmask, ldmask, rdmask):

    n = len(board)

    # All_rows_filled is a bit mask
    # having all N bits set
    all_rows_filled = (1 << n) - 1

    # If rowmask will have all bits set, means
    # queen has been placed successfully
    # in all rows and board is displayed
    if (rowmask == all_rows_filled):
        v = []
        for i in board:
            for j in range(len(i)):
                if i[j] == 'Q':
                    v.append(j+1)
        result.append(v)

    # We extract a bit mask(safe) by rowmask,
    # ldmask and rdmask. all set bits of 'safe'
    # indicates the safe column index for queen
    # placement of this iteration for row index(row).
    safe = all_rows_filled & (~(rowmask | ldmask | rdmask))

    while (safe > 0):

        # Extracts the right-most set bit
        # (safe column index) where queen
        # can be placed for this row
        p = safe & (-safe)
        col = (int)(math.log(p)/math.log(2))
        board[row][col] = 'Q'

        # This is very important:
        # we need to update rowmask, ldmask and rdmask
        # for next row as safe index for queen placement
        # will be decided by these three bit masks.

        # We have all three rowmask, ldmask and
        # rdmask as 0 in beginning. Suppose, we are placing
        # queen at 1st column index at 0th row. rowmask, ldmask
        # and rdmask will change for next row as below:

        # rowmask's 1st bit will be set by OR operation
        # rowmask = 00000000000000000000000000000010

        # ldmask will change by setting 1st
        # bit by OR operation  and left shifting
        # by 1 as it has to block the next column
        # of next row because that will fall on left diagonal.
        # ldmask = 00000000000000000000000000000100

        # rdmask will change by setting 1st bit
        # by OR operation and right shifting by 1
        # as it has to block the previous column
        # of next row because that will fall on right diagonal.
        # rdmask = 00000000000000000000000000000001

        # these bit masks will keep updated in each
        # iteration for next row
        solveBoard(board, row+1, rowmask | p, (ldmask | p) << 1, (rdmask | p) >> 1)

        # Reset right-most set bit to 0 so, next
        # iteration will continue by placing the queen
        # at another safe column index of this row
        safe = safe & (safe-1)

        # Backtracking, replace 'Q' by ' '
        board[row][col] = ' '

# Program to print board
def printBoard(board):
    for row in board:
        print("|" + "|".join(row) + "|")

# Driver Code
def n_queen_solution_by_n(n):

    board = []

    for _ in range(n):
        row = []
        for _ in range(n):
            row.append(' ')
        board.append(row)

    rowmask = 0
    ldmask = 0
    rdmask = 0
    row = 0

    # Function Call
    result.clear()
    solveBoard(board, row, rowmask, ldmask, rdmask)
    result.sort()

    return result