import math
import random

WIN_LINES = [
    [(0,0),(0,1),(0,2)],  # rows
    [(1,0),(1,1),(1,2)],
    [(2,0),(2,1),(2,2)],
    [(0,0),(1,0),(2,0)],  # cols
    [(0,1),(1,1),(2,1)],
    [(0,2),(1,2),(2,2)],
    [(0,0),(1,1),(2,2)],  # diagonals
    [(0,2),(1,1),(2,0)]
]


class GameBoard:

    def __init__(self):

        self.entries = [[0, 0, 0], [0, 0, 0], [0, 0 ,0]]
        

    def print_bd(self):

        for i in range(3):
            for j in range(3):
                print(self.entries[i][j],end='')
            print('')



    def checkwin(self) -> int:
        
        for line in WIN_LINES:
            vals = [self.entries[r][c] for r,c in line]
            if vals == [1, 1, 1]:   
                return 1
            if vals == [2, 2, 2]:
                return 2
            
        if any(0 in row for row in self.entries):
            return 0

        return 3
    
    def check_nextplayer(self, bd = None):
        count_1 = sum(cc == 1 for row in bd for cc in row)
        count_2 = sum(cc == 2 for row in bd for cc in row)
        return 1 if count_1 == count_2 else 2
    
    def play_move(self, move):
        self.entries[move[0]][move[1]] = self.check_nextplayer(self.entries)
    
    def getmoves(self):
        return [(r,c) for r in range(3) for c in range(3) if self.entries[r][c]==0] # all possible position where the board is empty
    
    def copy(self):
        new_board = GameBoard()
        new_board.entries = [row[:] for row in self.entries]
        return new_board
    
class MCTSNode:
    def __init__(self, bd: GameBoard, parent: None, action: None):
        self.bd = bd             
        self.parent = parent
        self.action = action # action that led to this node          
        self.children = [] # list of child nodes
        self.possible_moves = bd.getmoves()  # moves that can be played from this node
        self.visits = 0
        self.wins = 0.0         

    def is_fully_expanded(self):
        return len(self.possible_moves) == 0
    
    def is_terminal(self):
        return self.bd.checkwin() != 0
    
def apply_action(bd:GameBoard, action, player):
        r,c = action        
        new_bd = bd.copy()
        new_bd.entries[r][c] = player
        return new_bd

class MCTS:
    def __init__(self, c = math.sqrt(2)):
        self.c = c

    
    
    
    def uct_select(self, node:MCTSNode, c = None) -> MCTSNode:
        # node: current node
        # return: child node with highest UCT value
        if c is None:
            c = self.c
        return max(node.children, key=lambda child: (child.wins / child.visits) + c*math.sqrt(math.log(node.visits)/child.visits))

    def expand(self, node:MCTSNode) -> MCTSNode:
        # node: current node
        # return: new child node after applying one of the possible moves

        action = node.possible_moves.pop()
        r,c = action

        child_bd = node.bd.copy()
        player = child_bd.check_nextplayer(child_bd.entries)
        child_bd = apply_action(child_bd, action, player)

        child_node = MCTSNode(child_bd, parent=node, action = action)
        node.children.append(child_node)
        return child_node
    
    def rollout(self,bd:GameBoard) -> int:
        # bd: current board
        # return: score on the same (+1: for winner player)
        
        rollout_bd = bd.copy()

        while rollout_bd.checkwin() == 0:
            next_player = rollout_bd.check_nextplayer(rollout_bd.entries)
            actions = rollout_bd.getmoves()
            if not actions:
                break
            action =random.choice(actions)
            rollout_bd = apply_action(rollout_bd, action, next_player)
        
        winner = rollout_bd.checkwin()
        if winner ==1 or winner ==2:
            return +1
        else:
            return 0
        
    def backpropagate(self, node:MCTSNode, reward:int):
        current = node
        while current is not None:
            current.visits += 1
            current.wins += reward
            # switch perspective
            reward = -reward

            #propagate to parent
            current = current.parent
    
    def search(self,root:MCTSNode, iter = 2000):
        # based on the rood board, run MCTS and return the best action
        #root = MCTSNode(root_bd, parent=None, action=None)
        root_bd = root.bd
        if root_bd.checkwin() != 0:
            raise ValueError("Game is over")
        
        for _ in range(iter):
            node = root

            # selection
            while (not node.is_terminal()) and node.is_fully_expanded():
                node = self.uct_select(node, c= self.c)
            
            # expansion
            if (not node.is_terminal()) and (not node.is_fully_expanded()):
                node = self.expand(node)

            # simulation 
            reward = self.rollout(node.bd)

            # backpropagation
            self.backpropagate(node, reward)
        self.c = 0
        best_child = self.uct_select(root,c=0)
        return best_child.action

    
def get_validated_input(prompt, valid_choices, transform = lambda x: x):
    while True:
        try:
            player_input = transform(input(prompt))
            if player_input in valid_choices:
                return player_input
            else:
                print(player_input)
                raise Exception("Invalid Input")
        except:
            print("Bad Input, please try again.")


if __name__ == "__main__":
    bd = GameBoard()
    start_choice = get_validated_input("Choose what you want to play (1, 2): ", [1, 2], lambda x: int(x))
    if start_choice == 1:
        player = "human"
    else:
        player = "bot"

    mcts = MCTS()
    
    
    while (state := bd.checkwin()) == 0:
        if player == "human":
            move = get_validated_input("Enter your move (x, y): ", bd.getmoves(), lambda x: tuple(map(int, map(str.strip, x.split(',')))))
            bd.play_move(move)
            player = "bot"
        else:
            
            root_node = MCTSNode(bd, parent= None, action=None)
    
            best_action = mcts.search(root_node, iter=20)
            print(f"The robot plays {best_action}")
            next_player = bd.check_nextplayer(bd.entries)
            bd = apply_action(bd, best_action, next_player)

            player = "human"
        bd.print_bd()
    if state == 1:
        print("1 won!")
    elif state == 2:
        print("2 won!")
    else:
        print("tie!")
    
