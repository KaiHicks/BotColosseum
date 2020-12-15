from collections import namedtuple

import numpy as np

from colosseum.games.game import GameTracker

Move = namedtuple('Move', ['player', 'horizontal', 'row', 'col'])

class ImmutableArray:
	"""
	A wrapper for a numpy array that exposes acceesses but not modifications.
	
	There will be ways to circumvent this through __getitem__ if the array is
	multidimensional. However, you can always just modify self._a since python
	has no formal access control. This is simply to discourage modifications. 
	"""
	def __init__(self, a:np.ndarray):
		self._a = a
	
	def __getitem__(self, i):
		return self._a[i]
	
	def __iter__(self):
		return iter(self._a)
	
	def __len__(self):
		return len(self._a)
	
	def __str__(self):
		return str(self._a)
	
	@property
	def shape(self):
		return self._a.shape


class DnBTracker(GameTracker):
	def __init__(self, playerid:int=-1, n:int=5, **kwargs):
		super().__init__(n_players=2)
		"""
		params:
			n:int=5 - Side length of the board
			playerid:int=-1 - The id of the player that created this tracker. 
				If the tracker was created by the host, the id is -1 (default).
		"""
		assert n>1, f'n must be greater than 1 (given {n})!'
		
		self._n = n
		self._hlines = np.zeros(shape=(self._n, self._n-1), dtype=np.int32)
		self._vlines = np.zeros(shape=(self._n-1, self._n), dtype=np.int32)
		self._boxes = -np.ones(shape=(self._n-1, self._n-1), dtype=np.int32)
		self._moves = 0
		
		self._playerid = playerid
		self._latest_move = None
		self._turn = 0
	
	# Getters
	@property
	def n(self)->int:
		return self._n
	
	@property
	def playerid(self)->int:
		return self._playerid
	
	@property
	def latest_move(self)->Move:
		return self._latest_move
	
	@property
	def moves(self)->int:
		return self._moves
	
	@property
	def whose_turn(self)->int:
		return self._turn
	
	@property
	def is_done(self)->bool:
		return self._moves >= 2*(self._n-1)*(self._n-2)
	
	@property
	def hlines(self)->ImmutableArray:
		"""
		Array containing the state of the horizontal lines (1 if filled in, 0 
		otherwise)
		"""
		return ImmutableArray(self._hlines)
	
	@property
	def vlines(self)->ImmutableArray:
		"""
		Array containing the state of the vertical lines (1 if filled in, 0 
		otherwise)
		"""
		return ImmutableArray(self._vlines)
	
	@property
	def boxes(self)->ImmutableArray:
		"""
		Array containing the state of the boxes --- captured or not. Each box
		is -1 if it is uncaptured and if the box is captured, it will contain 
		the id of the player that captured it
		"""
		return ImmutableArray(self._boxes)
	
	# Behavior
	
	def edges_left(self, row:int, col:int)->int:
		"""
		Returns the number of edges left to capture (row, col).
		"""
		if not (0 <= row <= self._n-1 and 0 <= col <= self._n-1):
			return -1
		return 4 - (self._hlines[row][col] + self._hlines[row+1][col]
			+ self._vlines[row][col] + self._vlines[row][col+1])
	
	def check_move(self, horizontal:bool, row:int, col:int)->bool:
		"""
		Returns True if the move is valid
		"""
		# Check bounds
		if horizontal:
			if not (0 <= row < self._n-1) or not (0 <= col < self._n):
				return False
		else:
			if not (0 <= row < self._n) or not (0 <= col < self._n-1):
				return False
		
		a = self._hlines if horizontal else self._vlines
		return 1-a[row][col]
	
	def make_move(self, horizontal:bool, row:int, col:int):
		"""
		params:
			horizontal:bool - True if the move is a horizontal line
			row:int, col:int - The position of the move
		"""
		assert self.check_move(horizontal, row, col), \
			f'The move {"h" if horizontal else "v"}{row},{col} is invalid!'
		return {'horizontal': horizontal, 'row':row, 'col':col}
	
	def update(self, player:int, horizontal:bool, row:int, col:int):
		"""
		params:
			player:int - The id of the player that made the move
			horizontal:bool - True if the move was horizontal
			row:int, col:int - The position of the move
		"""
		assert self.check_move(horizontal, row, col), \
			f'The move {"h" if horizontal else "v"}{row} {col} is invalid!'
		
		a = self._hlines if horizontal else self._vlines
		a[row][col] = 1
		
		pts_gained = 0
		if horizontal:
			otherrow = row-1
			othercol = col
		else:
			otherrow = row
			othercol = col-1
		if self.edges_left(row, col) == 0:
			pts_gained += 1
			self._boxes[row, col] = player
		if self.edges_left(otherrow, othercol) == 0:
			pts_gained += 1
			self._boxes[otherrow, othercol] = player
		self.points[self._turn] += pts_gained
		if not pts_gained:
			self._turn = (self._turn + 1)%self._n_players
		
		self._moves += 1
		self._latest_move = Move(player, horizontal, row, col)
	
	def render(self)->str:
		"""
		Renders a string representation of the board for printing
		"""
		# Start with the board
		hline = '---'
		vline = ' | '
		dot = ' • '
		blank = '   '
		def v2l(val, line):
			return line if val == 1 else blank
		
		lines1 = []
		lines2 = []
		# Prepare all even rows with horizontal lines
		for line in self._hlines:
			lines1.append(dot + dot.join(v2l(c, hline) for c in line) + dot)
		# Prepare all odd rows with the vertical lines
		for line, boxes in zip(self._vlines, self._boxes):
			s = ''
			for col, box in zip(line, boxes):
				s += v2l(col, vline) + (blank if box < 0 else f' {box} ')
			lines2.append(s)
		
		lines = [lines1[0],]
		for l1, l2 in zip(lines1[1:], lines2):
			lines.append(l2)
			lines.append(l1)
		
		board = '\n'.join(lines)
		
		# Now for the status
		status = f'| Score: {self.points[0]}-{self.points[1]}   Player ' \
			f'{self._turn}\'s turn |'
		bars = f'+{"-"*(len(status)-2)}+'
		
		return '\n'.join([board, bars, status, bars])