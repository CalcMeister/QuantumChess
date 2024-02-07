import chess

verbosity = 0


NormalChessGame = chess.GameInstance()
move_log = []

while True:
	chess.visualize(NormalChessGame.current_board)
	move = input("Input a move: ")
	move_log.append(move)

	if move == 'exit':
		break

	start_square = move[:2]
	end_square = move[2:]

	NormalChessGame.log_move((start_square, end_square))
	legal = NormalChessGame.commit_moves()

	if not legal:
		break