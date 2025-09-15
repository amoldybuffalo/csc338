import copy
board = [
    [0,0,0],
    [0,0,0],
    [0,0,0],
]

def print_board(board):
    for i in range(3):
        for j in range(3):
            print(f"{board[i][j]} ", end="")
        print("")
    print("\n")

def won(board):
    for i in range(3):
        if board[i][0] != 0:
            if board[i][0] == board[i][1] == board[i][2]:
                return True
        if board[0][i] != 0:
            if board[0][i] == board[1][i] == board[2][i]:
                return True
    if board[0][0] != 0:
        if board[0][0] == board[1][1] == board[2][2]:
            return True
    if board[2][0] != 0:
        if board[2][0] == board[1][1] == board[0][2]:
            return True

    return False    

def full(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return False
    return True

def possible_moves(board, to_play):
    possibilities = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                b = copy.deepcopy(board)
              
                b[i][j] = to_play
                possibilities.append(b)
        
    return possibilities, "O" if to_play == "X" else "X"
            

def calc_states(board, to_play):
    if won(board) or full(board):
        return 1
    else:
        sum = 0
        moves, to_play = possible_moves(board, to_play)
        for move in moves:
            sum += calc_states(move, to_play)
        return sum
print(calc_states(board, "X"))