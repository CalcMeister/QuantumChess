from copy import deepcopy
import colored
#import re
import toolz
from collections import Counter
import uuid

#Assume a standard 8x8 chessboard with a standard set of pieces.

global verbose
verbose = 0

###Classes

class ChessPiece:
	def __init__(self, color, chessman):
		colors = ('white', 'black')
		chessmen = ('king', 'queen', 'rook', 'bishop', 'knight', 'pawn')

		if color not in colors or chessman not in chessmen:
			raise ValueError('Invalid piece color or type.')

		self.color = color
		self.chessman = chessman
		self.full_name = self.color + ' ' + self.chessman
		self.id = uuid.uuid4()

	def __hash__(self):
		return hash(self.id)

	def __eq__(self, other):
		'''
		Testing equality will return True is pieces are the same type and color, even
		if they have different IDs. Use is to compare objects, or compare IDs directly.
		'''
		if isinstance(other, ChessPiece):
			return self.full_name == other.full_name
		else:
			return False

class BoardState:
	def __init__(self, **kwargs):
		default_start = [
			[ChessPiece('white', 'rook'),	ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'rook')],
			[ChessPiece('white', 'knight'), ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'knight')],
			[ChessPiece('white', 'bishop'), ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'bishop')],
			[ChessPiece('white', 'queen'), 	ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'queen')],
			[ChessPiece('white', 'king'), 	ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'king')],
			[ChessPiece('white', 'bishop'), ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'bishop')],
			[ChessPiece('white', 'knight'), ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'knight')],
			[ChessPiece('white', 'rook'), 	ChessPiece('white', 'pawn'), None, None, None, None, ChessPiece('black', 'pawn'), ChessPiece('black', 'rook')]
		]

		self.board = kwargs.get('board', default_start)
		self.last_move = kwargs.get('last_move', -1)

	def __hash__(self):
		return hash(tuple(tuple(file) for file in self.board))

	def __eq__(self, other):
		return self.board == other.board

	def square(self, coordinate):
		'''
		Returns the name of the piece on a square. None if None.
		'''
		return self.board[coordinate[0]][coordinate[1]]

	def set_last_move(self, move_number):
		'''
		Sets the value for the last move that was played.
		'''
		self.last_move = move_number

	def increment_last_move(self):
		'''
		Increments the last move.
		'''
		self.last_move += 1

	def set_square(self, coordinate, piece: ChessPiece):
		'''
		Set a square to be a piece or None.
		'''
		if isinstance(piece, ChessPiece) or piece is None:
			self.board[coordinate[0]][coordinate[1]] = piece
		else:
			raise TypeError('Squares must contain either a Piece or None.')

class GameInstance:
	def __init__(self, **kwargs):
		self.record = kwargs.get('record', [])
		self.starting_board = kwargs.get('starting_board', BoardState())
		self.current_board = kwargs.get('current_board', self.starting_board)

	def log_move(self, move):
		'''
		Adds a move to the record. Does not check if the move was legal or advance the
		state of the board.
		THIS is where letters stop. Only ((a, b) (x, y)) formatted moves.
		'''
		self.record.append(move)

	def commit_moves(self, **kwargs):
		'''
		Plays through the game as referenced in the record, with changes reflecting
		in current_board. Returns True if all moves were legal and False if otherwise.
		'''
		check_for_legality = kwargs.get('check_for_legality', True)

		start_index = int(self.current_board.last_move + 1)

		for move in self.record[start_index:]:
			
			if check_for_legality is False or is_legal_chess_move(self.current_board, move, record=self.record):
				piece_on_start_square = self.current_board.square(move[0])

				#okay this line is basically unreadable but I promise it is True if the move was an en passant
				if piece_on_start_square.chessman == 'pawn' and move[0][0] != move[1][0] and self.current_board.square(move[1]) is None:
					self.current_board.set_square((move[1][0], move[0][1]), None) #clever
				#if it was a castle
				if piece_on_start_square.chessman == 'king' and abs(move[0][0] - move[1][0]) == 2:
					castling_rook_pos = ({6:7, 2:0}[move[1][0]], {'black':7, 'white':0}[piece_on_start_square.color])
					castling_rook = self.current_board.square(castling_rook_pos)

					self.current_board.set_square(castling_rook_pos, None)
					self.current_board.set_square({6:5, 2:3}[move[1][0]]+{'black':7, 'white':0}[piece_on_start_square.color], castling_rook)

				self.current_board.set_square(move[1], self.current_board.square(move[0]))
				self.current_board.set_square(move[0], None)
				self.current_board.increment_last_move()
			else:
				return False

		return True

	def move(self, move):
		'''
		Adds one move to the log IF it is legal, then commits the log.
		Returns False if move is illegal and does not affect the log.
		Log cannot have uncommitted moves to run this.
		'''
		if self.current_board.last_move != len(self.record)-1:
			raise Exception('Log has uncommitted moves.')

		if is_legal_chess_move(self.current_board, move):
			self.log_move(move)
			self.commit_moves(check_for_legality=False)
			return True
		else:
			return False

class QuantumChessGame:
	def __init__(self):
		self.instances = [GameInstance()]

	def move(self, move):
		next_instances = []

		for instance in self.instances:
			new_instance = deepcopy(instance)
			if new_instance.move(move):
				next_instances.append(new_instance)

		if len(next_instances) == 0:
			raise Exception('Move is not legal in any universe.')
		else:
			self.instances = next_instances

		self.cull_duplicate_states()

	def superposition(self, square, **kwargs):
		next_instances = []

		piece_ID = kwargs.get('piece_ID', True) #Disambiguator for when there are multiple pieces on a square
		cull_duplicates = kwargs.get('cull_duplicates', True)

		for instance in self.instances:
			for rank in range(8):
				for file in range(8):
					new_instance = deepcopy(instance)
					if new_instance.move((square, (rank, file))):
						next_instances.append(new_instance)

		if len(next_instances) == 0:
			raise Exception('No valid moves from source square.')
		else:
			self.instances = next_instances

		self.cull_duplicate_states()

	def cull_duplicate_states(self):
		self.instances = list(toolz.unique(self.instances, key=lambda x: x.current_board))

###Funcs

def is_in_check(board, color):
	for king_x in range(8):
		for king_y in range(8):
			piece = board.square((king_x, king_y))
			if piece is not None and piece.color == color and piece.chessman == 'king':
				for x in range(8):
					for y in range(8):
						if is_legal_chess_move(board, ((x, y), (king_x, king_y)), check_for_check=False, allow_moves_out_of_turn=True):
							say(5, f'{color}\'s king is in check by the {board.square((x, y)).full_name} at {(x,y)}')
							return True

	return False

def is_legal_chess_move(board: BoardState, move, **kwargs) -> bool:
	'''
	Given a chess move notated as a start coordinate and an ending coordinate,
	return True if legal and False if illegal. Pawn promotions are going to be complicated.
	For now, I will assume that the move will be in the format [coordinate, coordinate]
	Monolithic function designed around the standard rules of chess.
	'''
	record = kwargs.get('record', None)
	check_for_check = kwargs.get('check_for_check', True)
	allow_moves_out_of_turn = kwargs.get('allow_moves_out_of_turn', False)
	allow_moves_in_place = kwargs.get('allow_moves_in_place', False)

	if check_for_check:
		board = deepcopy(board) #Need to do this for in-check testing.
	start_square = move[0]
	end_square = move[1]
	absolute_offset = (abs(start_square[0]-end_square[0]), abs(start_square[1]-end_square[1]))
	piece = board.square(start_square)
	captured_piece = board.square(end_square)
	is_castle = False
	is_en_passant = False
	verb_affector = 2*int(not(check_for_check))

	if piece is None:
		say(2+verb_affector, f'Move is illegal because start square {start_square} is empty.')
		return False

	piece_type = piece.chessman
	piece_color = piece.color
	opponent_color = {'white':'black', 'black':'white'}[piece_color]

	say(3+verb_affector, f'Checking if {piece_color}\'s {piece_type} at {start_square} can move to {end_square} where the piece is {str(captured_piece)}...')

	if not allow_moves_out_of_turn and {1:'white', 0:'black'}[board.last_move % 2] != piece_color:
		say(2+verb_affector, f'Move is illegal because {piece_color} cannot move out of turn.')
		return False

	if not allow_moves_in_place and start_square == end_square:
		say(2+verb_affector, 'Move is illegal because you cannot move to the same square you\'re on.')
		return False

	if captured_piece != None:
		if piece_color == captured_piece.color:
			say(2+verb_affector, 'Move is illegal because pieces cannot capture their own color.')
			return False

	if piece_type == 'pawn':
		if absolute_offset[0] == 0:
			if ((end_square[1]-start_square[1]) * {'white':1, 'black':-1}[piece_color]) not in (2, 1)[(start_square[1] != {'white':1, 'black':6}[piece_color]):]:
				say(2+verb_affector, 'Move is illegal because pawns can\'t move like that. (1)')
				return False
			if absolute_offset[1] == 2 and board.square((start_square[0], start_square[1]+{'white':1, 'black':-1}[piece_color])) is not None:
				say(2+verb_affector, 'Move is illegal because pawns cannot jump pieces.')
				return False
			if board.square(end_square) is not None:
				say(2+verb_affector, 'Move is illegal because pawns cannot capture forwards.')
				return False

		elif absolute_offset[0] == 1:
			if end_square[1]-start_square[1] != {'white':1, 'black':-1}[piece_color]:
				say(2+verb_affector, 'Move is illegal because pawns can\'t move like that. (2)')
				return False
			if captured_piece is None:
				en_passant_capture_square = (end_square[0], end_square[1]+{'white':-1, 'black':1}[piece_color])
				if end_square[1] == {'white':5, 'black':2}[piece_color] and board.square(en_passant_capture_square).full_name == f'{opponent_color} pawn': #attempted en passant
					is_en_passant = True
					if record is not None and record[board.last_move][1] != en_passant_capture_square:
						say(2+verb_affector, 'Move is illegal because en passant only works immediately following a pawn moving two squares forward.')
						return False
				else:
					say(2+verb_affector, 'Move is illegal because pawns can only move diagonally when capturing.')
					return False

		else:
			say(2+verb_affector, 'Move is illegal because pawns can\'t move like that. (3)')
			return False

	elif piece_type == 'rook':
		if min(absolute_offset) == 0:
			for i in range(1, max(absolute_offset)):
				if board.square(((start_square[0] + i*(absolute_offset[0] != 0)*(2*(end_square[1]>start_square[1])-1)), (start_square[1] + i*(absolute_offset[1] != 0)*(2*(end_square[1]>start_square[1])-1)))) is not None:
					say(2+verb_affector, 'Move is illegal because rooks cannot jump pieces.')
					return False
		else:
			say(2+verb_affector, 'Move is illegal because rooks must move along a rank or file.')
			return False

	elif piece_type == 'knight':
		if absolute_offset not in ((2, 1), (1, 2)):
			say(2+verb_affector, 'Move is illegal because knights can\'t move like that.')
			return False

	elif piece_type == 'bishop':
		if absolute_offset[0] != absolute_offset[1]:
			say(2+verb_affector, 'Move is illegal because bishops must move diagonally.')
			return False
		for i in range(1, absolute_offset[0]):
			if board.square((start_square[0] + i*(2*(end_square[0]>start_square[0])-1), start_square[1] + i*(2*(end_square[1]>start_square[1])-1))) is not None:
				say(2+verb_affector, 'Move is illegal because bishops cannot jump pieces.')
				return False

	elif piece_type == 'queen':
		if absolute_offset[0] == absolute_offset[1]:
			for i in range(1, absolute_offset[0]):
				if board.square((start_square[0] + i*(2*(end_square[0]>start_square[0])-1), start_square[1] + i*(2*(end_square[1]>start_square[1])-1))) is not None:
					say(2+verb_affector, 'Move is illegal because queens cannot jump pieces.')
					return False
		elif min(absolute_offset) == 0:
			for i in range(1, max(absolute_offset)):
				if board.square(((start_square[0] + i*(absolute_offset[0] != 0)*(2*(end_square[1]>start_square[1])-1)), (start_square[1] + i*(absolute_offset[1] != 0)*(2*(end_square[1]>start_square[1])-1)))) is not None:
					say(2+verb_affector, 'Move is illegal because queens cannot jump pieces.')
					return False
		else:
			say(2+verb_affector, 'Move is illegal because queens must move along a rank, file, or diagonal.')
			return False

	elif piece_type == 'king':
		if absolute_offset[1] == 0 and end_square[0] in (2, 6): #If it's an attempted castle
			is_castle = {6:'kingside', 2:'queenside'}[end_square[0]]

			if is_in_check(board, piece_color):
				say(2+verb_affector, 'Move is illegal because castles cannot occur out of check.')
				return False

			if board.square(({2:3, 6:5}[end_square[0]], end_square[1])) is not None:
				say(2+verb_affector, 'Move is illegal because there\'s a piece in the way of the castle.')
				return False

			if not is_legal_chess_move(board, (start_square, ({2:3, 6:5}[end_square[0]], end_square[1]))):
				say(2+verb_affector, 'Move is illegal because kings cannot castle through check.')
				return False

			if board.square(({'kingside':7, 'queenside':0}[is_castle], {'black':7, 'white':0}[piece_color])).full_name != f'{piece_color} rook':
				say(2+verb_affector, 'Move is illegal because there is no rook to castle with.')
				return False

			if record is not None:
				for m in record[:board.last_move + 1]:
					if m[0] == start_square:
						say(2+verb_affector, 'Move is illegal because the king has already moved and thus cannot castle.')
						return False
					if m[0] == ({'kingside':7, 'queenside':0}[is_castle], {'black':7, 'white':0}[piece_color]):
						say(2+verb_affector, 'Move is illegal because the rook involved in the castle has already moved.')
						return False

		elif max(absolute_offset) > 1:
			say(2+verb_affector, 'Move is illegal because kings can only move one square at a time.')
			return False

	else:
		say(2+verb_affector, 'Move is illegal because the piece type is unknown.')
		return False

	if check_for_check:
		say(2, 'Checking if king will be in check after move...')
		board.set_square(start_square, None)
		board.set_square(end_square, piece)
		board.increment_last_move()

		if is_castle:
			castling_rook_pos = {'kingside':7, 'queenside':0}[is_castle]+{'black':7, 'white':0}[piece_color]
			castling_rook = board.square(castling_rook_pos)

			board.set_square(castling_rook_pos, None)
			board.set_square({'kingside':5, 'queenside':3}[is_castle]+{'black':7, 'white':0}[piece_color], castling_rook)

		if is_en_passant:
			board.set_square(en_passant_capture_square, None)

		if is_in_check(board, piece_color):
			say(2, f'Move is illegal because {piece_color}\'s king would be in check.')
			return False

	say(2+verb_affector, 'Move is legal')
	return True

def say(msg_verbosity, message):
	if msg_verbosity <= verbose:
		print(message)

def visualize_superposition(quantum_game: QuantumChessGame, **kwargs):
	display_coordinates = kwargs.get('display_coordinates', True)
	record = kwargs.get('record', None)
	size = kwargs.get('size', 1) #Size of the displayed board, in character width of a square / 2

	black = colored.Fore.black
	white = colored.Fore.white
	beige = colored.Back.cyan
	tan = colored.Back.blue
	superpositioned = colored.Back.magenta

	icons = {'pawn':'p', 'rook':'r', 'knight':'n', 'bishop':'b', 'queen':'Q', 'king':'K'}
	fore_colors = {'white':white, 'black':black}
	spaces = ' ' * (size * 2)
	output = ''

	for y in range(7, -1, -1):
		
		if display_coordinates:
			output += str(y + 1)+' '

		for x in range(8):
			pieces_in_superposition = Counter([i.current_board.square((x,y)) for i in quantum_game.instances])

			if len(pieces_in_superposition) == 1:
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
				display_str += fore_colors[piece.color] + icons[piece.chessman]

			display_str += spaces[:size * 2 - len(pieces_in_superposition)]

			output += display_str

		output += colored.Style.reset+'\n'

	if display_coordinates:
		output += '  a b c d e f g h'

	print(output)

def current_turn(move_number):
	if move_number % 2:
		return 'white'
	else:
		return 'black'

def parse_algebraic_coordinate(coord_str):
	coord = [None, None]
	ranks = {'1':0, '2':1 ,'3':2 ,'4':3 ,'5':4 ,'6':5 ,'7':6 ,'8':7}
	files = {'a':0, 'b':1 ,'c':2 ,'d':3 ,'e':4 ,'f':5 ,'g':6 ,'h':7}
	say(5, f'Parsing coordinate string: \'{coord_str}\'')

	for char in coord_str:
		if char in ranks:
			coord[1] = ranks[char]
		elif char in files:
			coord[0] = files[char]

	return tuple(coord)

def test_coordinate_validity(move):
	try:
		for coord in move:
			for axis in coord:
				if axis not in range(8):
					raise ValueError('Bad coordinates.')
	except:
		raise ValueError('Incorrectly formatted coordinates.')

# def visualize(board: BoardState, **kwargs):
# 	display_coordinates = kwargs.get('display_coordinates', True)
# 	possible_moves = kwargs.get('possible_moves', None) #expecting coord for start square
# 	record = kwargs.get('record', None)
# 	size = kwargs.get('size', 'small')

# 	black = colored.Fore.black
# 	white = colored.Fore.white
# 	beige = colored.Back.cyan
# 	tan = colored.Back.blue
# 	possible = colored.Back.green
# 	source = colored.Back.red

# 	icons = {'pawn':'p ', 'rook':'r ', 'knight':'n ', 'bishop':'b ', 'queen':'Q ', 'king':'K ', 'empty':'  '}
# 	output = ''

# 	for y in range(7, -1, -1):
		
# 		if display_coordinates:
# 			output += str(y + 1)+' '

# 		for x in range(8):
# 			piece = board.square((x, y))

# 			if possible_moves is not None and is_legal_chess_move(board, (possible_moves, (x, y)), record=record):
# 				back = possible
# 			elif possible_moves is not None and possible_moves == (x, y):
# 				back = source
# 			elif abs(x % 2 - y % 2):
# 				back = beige
# 			else:
# 				back = tan

# 			if piece is None:
# 				piece = 'xxxxx empty'
# 			elif piece[:5] == 'white':
# 				fore = white
# 			else:
# 				fore = black

# 			output += back+fore+icons[square[6:]]
# 		output += colored.Style.reset+'\n'

# 	if display_coordinates:
# 		output += '  a b c d e f g h'

# 	print(output)

# def parse_alg_move(board, move):
# 	'''
# 	Parses proper Algebraic Notation, returning integer coordinates. ((a, b), (x, y))
# 	Will also passthrough integer coordinates.
# 	Expects proper capitalization.
# 	Hate that I have to do this, but it does have to check for move legality for it to work.
# 	Example moves:	Ra5#	Q3xe4	e6	axb3
# 	'''
# 	piece_names = {'Q':'queen', 'K':'king', 'R':'rook', 'B':'bishop', 'N':'knight'}

# 	parsed_move = ((None, None), (None, None))
# 	source_piece = None
# 	capture = False

# 	if isinstance(move, str):	#Algebraic notation
# 		if re.search('^[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8][+#!?]?$', move) is None:
# 			raise ValueError('Invalid algebraic notation.')

# 		trimmed_move = move.strip('!?+#')

# 		parsed_move[1] = parse_algebraic_coordinate(move[-2:])
# 		trimmed_move = move[:-2]
# 		if trimmed_move[-1] == 'x':
# 			trimmed_move = trimmed_move[:-1]
# 			capture = True

# 		if board.square(parsed_move[1]) != {}[]:
# 			raise ValueError('Invalid move: unexpected capture.')

# 		if move[0] in piece_names: #Not a pawn move
# 			source_piece = current_turn(board.last_move) + ' ' + piece_names[move[0]]
# 			trimmed_move = trimmed_move[1:]

# 		elif len(trimmed_move) == 2: #Not a pawn move (implicit)
# 			parsed_move[0] = parse_algebraic_coordinate(trimmed_move)



# 	elif isinstance(move, (list, tuple)): #Explicit coordinates
# 		try:
# 			for coord in move:
# 				for axis in coord:
# 					if not (isinstance(axis, int) and axis in range(8)):
# 						raise ValueError('Invalid explicit coordinates.')
# 			return move
# 		except:
# 			raise ValueError('Invalid explicit coordinate format.')

# 	else:
# 		raise TypeError('Moves must be encoded in a string, tuple, or list.')