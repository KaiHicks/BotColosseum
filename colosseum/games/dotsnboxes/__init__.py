"""
-- Dots and Boxes --
An n x n grid of dots is drawn and two players take turns connecting adjacent 
dots. If the line that a player draws completes a square, said square (or box)
is considered captured by the player. The player is then awarded an extra turn.
When all adjacent dots have been connected, the number of boxes that each 
player captured is counted and the player with the highest number of captures 
wins. 
"""

import numpy as np

from colosseum.games.game import GameTracker, GameHoster

class DnBTracker(GameTracker):
	def __init__(self, n:int=5, playerid:int=-1):
		super().__init__(n_players=2)
		"""
		params:
			n_players:int - Number of players
			n:int=5 - Side length of the board
			playerid:int=-1 - The id of the player that created this tracker. 
				If the tracker was created by the host, the id is -1 (default).
		"""
		assert n>1, f'n must be greater than 1 (given {n})!'
		
		self._n = n
		self._hlines = np.zeros(shape=(self._n, self._n-1))
		self._vlines = np.zeros(shape=(self._n-1, self._n))
		
		self._turn = 0
		self._is_done = False
	
	def edges_left(self, row:int, col:int)->int:
		"""
		Returns the number of edges left to capture (row, col).
		"""
		assert 0 <= row <= self._n-1 and 0 <= col <= self._n-1
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
			pts_gained += 1 if self.edges_left(row-1, col) == 0 \
				else 0
			pts_gained += 1 if self.edges_left(row, col) == 0 \
				else 0
		else:
			pts_gained += 1 if self.edges_left(row, col-1) == 0 \
				else 0
			pts_gained += 1 if self.edges_left(row, col) == 0 \
				else 0
		self.points[self._turn] += pts_gained
		if not pts_gained:
			self._turn = (self._turn + 1)%self._n_players
	
	def render(self)->str:
		"""
		Renders a string representation of the board for printing
		"""
		hline = '---'
		vline = ' | '
		dot = ' • '
		blank = '   '
		def v2l(val, line):
			return line if val == 1 else blank
		
		lines1 = []
		lines2 = []
		for line in self._hlines:
			lines1.append(dot + dot.join(v2l(c, hline) for c in line) + dot)
		for line in self._vlines:
			lines2.append(blank.join(v2l(c, vline) for c in line))
		
		lines = [lines1[0],]
		for l1, l2 in zip(lines1[1:], lines2):
			lines.append(l2)
			lines.append(l1)
		
		return '\n'.join(lines)
	
	@property
	def whose_turn(self):
		return self._turn
	
	@property
	def is_done(self):
		return self._is_done

class DnBHoster(GameHoster):
	def play(self, rows, cols)->DnBTracker:
		"""
		params:
			upper:int - Exclusive upper bound of the secret number
			lower:int=0 - Inclusive lower bound of the secret number
		returns: 
			GTNTracker - The GameTracker for this game
		"""
		game = DnBTracker(len(self._players))
		
		for i, p in enumerate(self._players):
			p.new_game({'playerid': i, 'n_players': len(self._players)})
		
		return game
	
	def _broadcast(self, player:int):
		"""
		Updates all players to the new gamestate. Called after every move. 
		params:
			player:int - The id of the player that made the guess
			guess:int - The guess the bot made
			higher:bool - If True, the true value is higher than the guess
			correct: - If True, the guess was correct
		"""
		for p in self._players:
			p.update(player=player)
