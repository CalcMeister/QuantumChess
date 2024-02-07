from copy import deepcopy
import colored

#Assume a standard 8x8 chessboard with a standard set of pieces. Game record is encoded in PGN.

class BoardState:
	def __init__(self, board=None, last_move=-1):
		default_start = [
			["white rook","white pawn",None,None,None,None,"black pawn","black rook"],
			["white knight","white pawn",None,None,None,None,"black pawn","black knight"],
			["white bishop","white pawn",None,None,None,None,"black pawn","black bishop"],
			["white queen","white pawn",None,None,None,None,"black pawn","black queen"],
			["white king","white pawn",None,None,None,None,"black pawn","black king"],
			["white bishop","white pawn",None,None,None,None,"black pawn","black bishop"],
			["white knight","white pawn",None,None,None,None,"black pawn","black knight"],
			["white rook","white pawn",None,None,None,None,"black pawn","black rook"]
		]

		if board is None:
			self.board = default_start
		else:
			self.board = board

		self.last_move = last_move

	def parse_coordinate(self, coordinate):
		"""
		Turns string coordinates (such as 'f5') into list indices.
		"""
		say(6, f'Parsing coordinate: {coordinate}')
		columns = {'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7}
		try:
			if isinstance(coordinate, str):
				return (columns[coordinate[0].lower()], int(coordinate[1])-1)
			else:
				return tuple(coordinate)
		except:
			raise ValueError("Bad coordinates.")

	def square(self, coordinate):
		"""
		Returns the name of the piece on a square. None if None.
		"""
		coordinate = self.parse_coordinate(coordinate)
		return self.board[coordinate[0]][coordinate[1]]

	def set_last_move(self, move_number):
		"""
		Sets the value for the last move that was played.
		"""
		self.last_move = move_number

	def increment_last_move(self):
		"""
		Increments the last move.
		"""
		self.last_move += 1

	def set_square(self, coordinate, piece):
		"""
		Set a square to be a piece or None.
		"""
		coordinate = self.parse_coordinate(coordinate)
		self.board[coordinate[0]][coordinate[1]] = piece

class GameInstance:
	def __init__(self, record=None, starting_board=BoardState(), current_board=None):
		"""
		The GameInstance class does not check that current_board is valid
		upon instantiation. These can be checked against the record using validate_record.
		"""

		if record is None:
			self.record = []
		else:
			self.record = record

		if current_board is None:
			self.current_board = starting_board
		else:
			self.current_board = current_board

		self.starting_board = starting_board

	def log_move(self, move):
		"""
		Adds a move to the record. Does not check if the move was legal or advance the
		state of the board.
		THIS is where letters stop. Only ((a, b) (x, y)) formatted moves.
		"""
		self.record.append((self.current_board.parse_coordinate(move[0]), self.current_board.parse_coordinate(move[1])))

		return True

	def commit_moves(self):
		"""
		Plays through the game as referenced in the record, with changes reflecting
		in current_board. Returns True if all moves were legal and False if otherwise.
		"""
		start_index = int(self.current_board.last_move + 1)

		for move in self.record[start_index:]:
			
			if is_legal_chess_move(self.current_board, move, record=self.record):
				start_square = self.current_board.square(move[0])

				#okay this line is basically unreadable but I promise it is True if the move was an en passant
				if start_square[6:] == 'pawn' and move[0][0] != move[1][0] and self.current_board.square(move[1]) is None:
					self.current_board.set_square((move[1][0], move[0][1]), None) #clever
				#if it was a castle
				if start_square[6:] == 'king' and abs(move[0][0] - move[1][0]) == 2:
					self.current_board.set_square({6:'h', 2:'a'}[move[1][0]]+{'black':'8', 'white':'1'}[start_square[:5]], None)
					self.current_board.set_square({6:'f', 2:'d'}[move[1][0]]+{'black':'8', 'white':'1'}[start_square[:5]], f'{start_square[:5]} rook')

				self.current_board.set_square(move[1], self.current_board.square(move[0]))
				self.current_board.set_square(move[0], None)
				self.current_board.increment_last_move()
			else:
				return False

		return True

def is_in_check(board, color):
	for king_x in range(8):
		for king_y in range(8):
			if board.square((king_x, king_y)) == color + " king":
				for x in range(8):
					for y in range(8):
						if is_legal_chess_move(board, ((x, y), (king_x, king_y)), check_for_check=False, allow_moves_out_of_turn=True):
							say(5, f"{color}'s king is in check by the {board.square((x, y))} at {(x,y)}")
							return True

	return False

def is_legal_chess_move(board: BoardState, move, **kwargs) -> bool:
	"""
	Given a chess move notated as a start coordinate and an ending coordinate,
	return True if legal and False if illegal. Pawn promotions are going to be complicated.
	For now, I will assume that the move will be in the format [coordinate, coordinate]
	Monolithic function designed around the standard rules of chess.
	"""
	record = kwargs.get('record', None)
	check_for_check = kwargs.get('check_for_check', True)
	allow_moves_out_of_turn = kwargs.get('allow_moves_out_of_turn', False)
	allow_moves_in_place = kwargs.get('allow_moves_in_place', False)

	if check_for_check:
		board = deepcopy(board) #Need to do this for in-check testing.
	start_square = board.parse_coordinate(move[0])
	end_square = board.parse_coordinate(move[1])
	absolute_offset = (abs(start_square[0]-end_square[0]), abs(start_square[1]-end_square[1]))
	piece = board.square(start_square)
	captured_piece = board.square(end_square)
	is_castle = False
	is_en_passant = False
	verb_affector = 2*int(not(check_for_check))
	if isinstance(move, str):
		move = (board.parse_coordinate(move[:2]), board.parse_coordinate(move[2:]))

	if piece is None:
		say(2+verb_affector, f"Move is illegal because start square {start_square} is empty.")
		return False

	piece_type = piece[6:]
	piece_color = piece[:5]
	opponent_color = {'white':'black', 'black':'white'}[piece_color]

	say(3+verb_affector, f"Checking if {piece_color}'s {piece_type} at {start_square} can move to {end_square} where the piece is {str(captured_piece)}...")

	if not allow_moves_out_of_turn and {1:'white', 0:'black'}[board.last_move % 2] != piece_color:
		say(2+verb_affector, f"Move is illegal because {piece_color} cannot move out of turn.")
		return False

	if start_square == end_square:
		say(2+verb_affector, "Move is illegal because you cannot move to the same square you're on.")
		return False

	if captured_piece != None:
		if piece_color == captured_piece[:5]:
			say(2+verb_affector, "Move is illegal because pieces cannot capture their own color.")
			return False

	if piece_type == "pawn":
		if absolute_offset[0] == 0:
			if ((end_square[1]-start_square[1]) * {'white':1, 'black':-1}[piece_color]) not in (2, 1)[(start_square[1] != {'white':1, 'black':6}[piece_color]):]:
				say(2+verb_affector, "Move is illegal because pawns can't move like that. (1)")
				return False
			if absolute_offset[1] == 2 and board.square((start_square[0], start_square[1]+{'white':1, 'black':-1}[piece_color])) is not None:
				say(2+verb_affector, "Move is illegal because pawns cannot jump pieces.")
				return False
			if board.square(end_square) is not None:
				say(2+verb_affector, "Move is illegal because pawns cannot capture forwards.")
				return False

		elif absolute_offset[0] == 1:
			if end_square[1]-start_square[1] != {'white':1, 'black':-1}[piece_color]:
				say(2+verb_affector, "Move is illegal because pawns can't move like that. (2)")
				return False
			if captured_piece is None:
				en_passant_capture_square = (end_square[0], end_square[1]+{'white':-1, 'black':1}[piece_color])
				if end_square[1] == {'white':5, 'black':2}[piece_color] and board.square(en_passant_capture_square) == f'{opponent_color} pawn': #attempted en passant
					is_en_passant = True
					if record is not None and board.parse_coordinate(record[board.last_move][1]) != en_passant_capture_square:
						say(2+verb_affector, "Move is illegal because en passant only works immediately following a pawn moving two squares forward.")
						return False
				else:
					say(2+verb_affector, "Move is illegal because pawns can only move diagonally when capturing.")
					return False

		else:
			say(2+verb_affector, "Move is illegal because pawns can't move like that. (3)")
			return False

	elif piece_type == "rook":
		if min(absolute_offset) == 0:
			for i in range(1, max(absolute_offset)):
				if board.square(((start_square[0] + i*(absolute_offset[0] != 0)*(2*(end_square[1]>start_square[1])-1)), (start_square[1] + i*(absolute_offset[1] != 0)*(2*(end_square[1]>start_square[1])-1)))):
					say(2+verb_affector, "Move is illegal because rooks cannot jump pieces.")
					return False
		else:
			say(2+verb_affector, "Move is illegal because rooks must move along a rank or file.")
			return False

	elif piece_type == "knight":
		if absolute_offset not in ((2, 1), (1, 2)):
			say(2+verb_affector, "Move is illegal because knights can't move like that.")
			return False

	elif piece_type == "bishop":
		if absolute_offset[0] != absolute_offset[1]:
			say(2+verb_affector, "Move is illegal because bishops must move diagonally.")
			return False
		for i in range(1, absolute_offset[0]):
			if board.square((start_square[0] + i*(2*(end_square[0]>start_square[0])-1), start_square[1] + i*(2*(end_square[1]>start_square[1])-1))) is not None:
				say(2+verb_affector, "Move is illegal because bishops cannot jump pieces.")
				return False

	elif piece_type == "queen":
		if absolute_offset[0] == absolute_offset[1]:
			for i in range(1, absolute_offset[0]):
				if board.square((start_square[0] + i*(2*(end_square[0]>start_square[0])-1), start_square[1] + i*(2*(end_square[1]>start_square[1])-1))) is not None:
					say(2+verb_affector, "Move is illegal because queens cannot jump pieces.")
					return False
		elif min(absolute_offset) == 0:
			for i in range(1, max(absolute_offset)):
				if board.square(((start_square[0] + i*(absolute_offset[0] != 0)*(2*(end_square[1]>start_square[1])-1)), (start_square[1] + i*(absolute_offset[1] != 0)*(2*(end_square[1]>start_square[1])-1)))):
					say(2+verb_affector, "Move is illegal because queens cannot jump pieces.")
					return False
		else:
			say(2+verb_affector, "Move is illegal because queens must move along a rank, file, or diagonal.")
			return False

	elif piece_type == "king":
		if absolute_offset[1] == 0 and end_square[0] in (2, 6): #If it's an attempted castle
			is_castle = {6:'kingside', 2:'queenside'}[end_square[0]]

			if is_in_check(board, piece_color):
				say(2+verb_affector, "Move is illegal because castles cannot occur out of check.")
				return False

			if board.square(({2:3, 6:5}[end_square[0]], end_square[1])) is not None:
				say(2+verb_affector, "Move is illegal because there's a piece in the way of the castle.")
				return False

			if not is_legal_chess_move(board, (start_square, ({2:3, 6:5}[end_square[0]], end_square[1]))):
				say(2+verb_affector, "Move is illegal because kings cannot castle through check.")
				return False

			if board.square(({'kingside':7, 'queenside':0}[is_castle], {'black':7, 'white':0}[piece_color])) != f'{piece_color} rook':
				say(2+verb_affector, "Move is illegal because there is no rook to castle with.")
				return False

			if record is not None:
				for m in record[:board.last_move + 1]:
					if board.parse_coordinate(m[0]) == start_square:
						say(2+verb_affector, "Move is illegal because the king has already moved and thus cannot castle.")
						return False
					if board.parse_coordinate(m[0]) == ({'kingside':7, 'queenside':0}[is_castle], {'black':7, 'white':0}[piece_color]):
						say(2+verb_affector, "Move is illegal because the rook involved in the castle has already moved.")
						return False

		elif max(absolute_offset) > 1:
			say(2+verb_affector, "Move is illegal because kings can only move one square at a time.")
			return False

	else:
		say(2+verb_affector, "Move is illegal because the piece type is unknown.")
		return False

	if check_for_check:
		say(2, "Checking if king will be in check after move...")
		board.set_square(start_square, None)
		board.set_square(end_square, piece)
		board.increment_last_move()

		if is_castle:
			board.set_square({'kingside':'h', 'queenside':'a'}[is_castle]+{'black':'8', 'white':'1'}[piece_color], None)
			board.set_square({'kingside':'f', 'queenside':'d'}[is_castle]+{'black':'8', 'white':'1'}[piece_color], f'{piece_color} rook')

		if is_en_passant:
			board.set_square(en_passant_capture_square, None)

		if is_in_check(board, piece_color):
			say(2, f"Move is illegal because {piece_color}'s king would be in check.")
			return False

	say(2+verb_affector, "Move is legal")
	return True

def say(msg_verbosity, message):
	#if msg_verbosity <= verbosity:
	if msg_verbosity <= 3:
		print(message)

def visualize(board: BoardState, **kwargs):
	display_coordinates = kwargs.get('display_coordinates', True)
	possible_moves = kwargs.get('possible_moves', None) #expecting coord for start square
	record = kwargs.get('record', None)
	size = kwargs.get('size', 'small')

	black = colored.Fore.black
	white = colored.Fore.white
	beige = colored.Back.cyan
	tan = colored.Back.blue
	possible = colored.Back.green

	icons = {"pawn":"p ", "rook":"r ", "knight":"k ", "bishop":"b ", "queen":"Q ", "king":"K ", "empty":"  "}
	output = ''

	for y in range(7, -1, -1):
		
		if display_coordinates:
			output += str(y + 1)+' '

		for x in range(8):
			square = board.square((x, y))

			if possible_moves is not None and (possible_moves == (x, y) or is_legal_chess_move(board, (board.parse_coordinate(possible_moves), (x, y)), record=record)):
				back = possible
			elif abs(x % 2 - y % 2):
				back = beige
			else:
				back = tan

			if square is None:
				square = 'xxxxx empty'
			elif square[:5] == "white":
				fore = white
			else:
				fore = black

			output += back+fore+icons[square[6:]]
		output += colored.Style.reset+'\n'

	if display_coordinates:
		output += '  a b c d e f g h'

	print(output)










