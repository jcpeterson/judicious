import judicious

# judicious.register("http://imprudent.herokuapp.com")

board = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

player1 = judicious.Person()
player2 = judicious.Person()

for _ in range(3):
    board = player1.chess(board=board)
    board = player2.chess(board=board)
