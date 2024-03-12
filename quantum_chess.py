import chess
import colored
import toolz

from copy import deepcopy
from collections import Counter

#Assume a standard 8x8 chessboard with a standard set of pieces.

global verbose
verbose = 0

###Classes

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

	def superposition(self, square, **kwargs):
		piece_ID = kwargs.get('piece_ID', True) #Disambiguator for when there are multiple pieces on a square
		cull_duplicates = kwargs.get('cull_duplicates', True)

		next_instances = []

		for instance in self.instances:
			for move in (m for m in instance.legal_moves if m.uci()[:2] == square):
				new_branch = instance.copy()
				new_branch.push(move)
				next_instances.append(new_branch)

		if len(next_instances) == 0:
			raise Exception('No valid moves from source square.')
		else:
			self.instances = next_instances

		self.cull_duplicate_states()

	def cull_duplicate_states(self):
		self.instances = list(toolz.unique(self.instances, key=lambda x: x.board_fen()))

###Funcs

def visualize_superposition(quantum_game: QuantumChessGame, **kwargs):
	display_coordinates = kwargs.get('display_coordinates', True)
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

	for y in range(7, -1, -1):
		
		if display_coordinates:
			output += str(y + 1)+' '

		for x in range(8):
			pieces_in_superposition = Counter([i.piece_map().get(chess.square(x, y), None) for i in quantum_game.instances])

			if len(pieces_in_superposition) <= 1:
				if abs(x % 2 - y % 2):
					back = beige
				else:
					back = tan

			elif len(pieces_in_superposition) > 1:
				back = superpositioned

			if None in pieces_in_superposition:
				pieces_in_superposition.pop(None)

			display_str = back
			for piece in tuple(pieces_in_superposition)[:size * 2]:
				display_str += fore_colors[piece.color] + icons[piece.piece_type]

			display_str += spaces[:size * 2 - len(pieces_in_superposition)]

			output += display_str

		output += colored.Style.reset+'\n'

	if display_coordinates:
		output += '  a b c d e f g h'

	print(output)