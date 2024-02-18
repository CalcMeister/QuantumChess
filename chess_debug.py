import chess

keyword = ''

while keyword != 'exit':

	command = input('>').split(' ')
	keyword = command[0]
	args = command[1:]

	if keyword == 'new':
		game = chess.GameInstance()

	elif keyword in ('b', 'board'):
		chess.visualize(game.current_board)

	elif keyword in ('m', 'move'):
		move = (chess.parse_algebraic_coordinate(args[0][:2]), chess.parse_algebraic_coordinate(args[0][2:]))
		if not game.move(move):
			print('Illegal move.')

	elif keyword == 'moves':
		chess.visualize(game.current_board, possible_moves=chess.parse_algebraic_coordinate(args[0]), record=game.record)

	elif keyword in ('v', 'verb', 'verbose'):
		chess.verbose = int(args[0])

	elif keyword == 'exit':
		continue

	else:
		print(f'-bash: {keyword}: command not found')