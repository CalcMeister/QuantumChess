import quantum_chess as ch

game = ch.QuantumChessGame()
#ch.verbose = 3

def plural_s(quantity):
	if quantity == 1:
		return ''
	else:
		return 's'

def print_stats():
	number_of_universes = len(game.instances)
	universes_in_check = [i for i,v in enumerate(game.instances) if v.is_check()]
	universes_in_checkmate = [i for i,v in enumerate(game.instances) if v.is_checkmate()]

	print(f'{number_of_universes} universe{plural_s(number_of_universes)} currently in superposition.')
	print(f'You are in check in {len(universes_in_check)} universe{plural_s(len(universes_in_check))}.')

while True:

	print_stats()


	# if len(universes_in_checkmate) > 0:
	# 	print('You have been checkmated. Look!')
	# 	for i in universes_in_checkmate:
	# 		ch.visualize_instance(game.instances[i])
	# 	break

	ch.visualize_instance(game.instances[0], show_colors=[True])

	move = input('Input a move:') #ex. d2d4 for normal moves, q d2 for quantum moves.

	if move == 'exit':
		break

	elif len(move) == 4: #Normal move.
		game.move(move)

	else:
		print('Unknown move.')

	game.superposition()
