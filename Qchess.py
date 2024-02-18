import chess as ch
from copy import deepcopy

#Quantum chess simulator using my chess library.

game = ch.QuantumChessGame()
#ch.verbose = 3

while True:
	for i in game.instances:
		ch.visualize(i.current_board)

	move = input('Input a move:') #ex. d2d4 for normal moves, q d2 for quantum moves.

	if move == 'exit':
		break

	if move[0] == 'q': #Placing a piece in a superposition between all its possible moves.
		start_square = ch.parse_algebraic_coordinate(move[-2:])
		print(start_square)
		game.superposition(start_square)

	elif len(move) == 4: #Normal move.
		start_square = ch.parse_algebraic_coordinate(move[:2])
		end_square = ch.parse_algebraic_coordinate(move[2:])
		game.move((start_square, end_square))

	else:
		print('Unknown move.\nex: \'d2d4\' for normal moves, \'q d2\' for quantum moves.')

	print(f'{len(game.instances)} universes currently in superposition.')
