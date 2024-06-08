#import chess
import chess
import colored

from toolz import unique
from copy import deepcopy
from collections import Counter

class QuantumChessGame:
	def __init__(self):
		self.instances = [chess.Board()]

	def move(self, move):
		next_instances = []

		for instance in self.instances:
			if move in (m.uci() for m in instance.legal_moves):
				instance.push(chess.Move.from_uci(move))
				next_instances.append(instance)

		# self.instances = [i.push(chess.Move.from_uci(move)) for i in self.instances if move in (m.uci() for m in i.legal_moves)]

		if len(next_instances) == 0:
			raise Exception('Move is not legal in any universe.')

		self.instances = next_instances

		self.cull_duplicate_states()

	def superposition(self, **kwargs):
		"""
		Branches the game tree between all possible moves from a specific square, all moves from any square, or some set of moves.
		"""
		cull_duplicates = kwargs.get('cull_duplicates', True)
		from_square = kwargs.get('from_square', None)
		set_of_moves = kwargs.get('set_of_moves', None)

		next_instances = []

		for instance in self.instances:
			moves = instance.legal_moves

			if set_of_moves is not None:
				moves = set_of_moves

			if from_square:
				moves = (m for m in moves if m.uci()[:2] == from_square) 

			for move in moves:
				new_branch = instance.copy()
				new_branch.push(move)
				next_instances.append(new_branch)

		if len(next_instances) == 0:
			raise Exception('No valid moves from source square.')
		else:
			self.instances = next_instances

		self.cull_duplicate_states()

	def cull_duplicate_states(self):
		self.instances = list(unique(self.instances, key=lambda x: x.board_fen()))

def visualize_superposition(quantum_game: QuantumChessGame, **kwargs):
	display_coordinates = kwargs.get('display_coordinates', True)
	display_taken_pieces = kwargs.get('display_taken_pieces', True)
	unicode_symbols = kwargs.get('unicode_symbols', True)
	size = kwargs.get('size', 1) #Size of the displayed board, in character width of a square / 2

	black = colored.Fore.black
	white = colored.Fore.white
	beige = colored.Back.cyan
	tan = colored.Back.blue
	superpositioned = colored.Back.magenta

	icons = {1:'p', 2:'n', 3:'b', 4:'r', 5:'Q', 6:'K'}
	fore_colors = {True:white, False:black}
	spaces = ' ' * (size * 2)
	output = ''

	piece_maps = [i.piece_map() for i in quantum_game.instances]
	pieces_in_superposition = {square:[m.get(square, None) for m in piece_maps] for square in range(64)}

	for y in range(7, -1, -1):
		
		if display_coordinates:
			output += str(y + 1)+' '

		for x in range(8):
			pieces_on_square = Counter(pieces_in_superposition[chess.square(x, y)])

			if len(pieces_on_square) <= 1:
				if abs(x % 2 - y % 2):
					back = beige
				else:
					back = tan

			elif len(pieces_on_square) > 1:
				back = superpositioned

			if None in pieces_on_square:
				pieces_on_square.pop(None)

			display_str = back
			for piece in tuple(pieces_on_square)[:size * 2]:
				piece_char = {True:piece.unicode_symbol(), False:icons[piece.piece_type]}[unicode_symbols]
				display_str += fore_colors[piece.color] + piece_char

			display_str += spaces[:size * 2 - len(pieces_on_square)]

			output += display_str

		output += colored.Style.reset+'\n'

		# if display_taken_pieces:
		# 	if y == 0:
		# 		disp
		# 	if y == 7:
		# 		disp

	if display_coordinates:
		output += '  a b c d e f g h'

	print(output)

def visualize_instance(board, **kwargs):
	display_coordinates = kwargs.get('display_coordinates', True)
	display_taken_pieces = kwargs.get('display_taken_pieces', True)
	unicode_symbols = kwargs.get('unicode_symbols', True)
	show_colors = kwargs.get('show_colors', [True, False]) #white, black

	black = colored.Fore.black
	white = colored.Fore.white
	beige = colored.Back.cyan
	tan = colored.Back.blue

	icons = {1:'p', 2:'n', 3:'b', 4:'r', 5:'Q', 6:'K'}
	fore_colors = {True:white, False:black}
	output = ''

	piece_map = board.piece_map()

	for y in range(7, -1, -1):
		
		if display_coordinates:
			output += str(y + 1)+' '

		for x in range(8):
			
			if abs(x % 2 - y % 2):
				back = beige
			else:
				back = tan

			piece = piece_map.get(chess.square(x,y), None)

			display_str = back

			if piece is not None and piece.color in show_colors:
				piece_char = {True:piece.unicode_symbol(), False:icons[piece.piece_type]}[unicode_symbols]
				display_str += fore_colors[piece.color] + piece_char + ' '
			else:
				display_str += '  '

			output += display_str

		output += colored.Style.reset+'\n'

		# if display_taken_pieces:
		# 	if y == 0:
		# 		disp
		# 	if y == 7:
		# 		disp

	if display_coordinates:
		output += '  a b c d e f g h'

	print(output)