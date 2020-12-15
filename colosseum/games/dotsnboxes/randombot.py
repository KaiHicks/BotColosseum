import random
from itertools import product

from colosseum.games.bot import Bot
from colosseum.games.dotsnboxes import DnBTracker, Move

class RandomBot(Bot):
	"""
	This bot will take random moves. 
	
	On new_game, a list of all possible moves will be generated and shuffled. 
	When the gamestate is updated (in update()), the latest move is removed 
	from the list. This is to prevent the same move being made twice. To take
	a turn, the last move in the list is simply returned. 
	"""
	
	def __init__(self):
		super().__init__(DnBTracker)
	
	def take_turn(self):
		move = self._moves[-1]
		return self.game.make_move(*move[1:])
	
	def update(self):
		latest_move = self.game.latest_move
		# Recreate the latest move but with our playerid
		latest_move = Move(self.game.playerid, latest_move.horizontal, 
			latest_move.row, latest_move.col)
		self._moves.remove(latest_move)
	
	def new_game(self):
		self._moves = []
		# A list of all possible horizontal moves
		horizontal_moves = [Move(self.game.playerid, True, row, col) 
			for row, col in product(range(self.game.n-1), range(self.game.n-2))]
		# A list of all possible vertical moves
		vertical_moves = [Move(self.game.playerid, False, row, col) 
			for row, col in product(range(self.game.n-2), range(self.game.n-1))]
		self._moves.extend(horizontal_moves)
		self._moves.extend(vertical_moves)
		# Shuffle the list of all possible moves
		random.shuffle(self._moves)

if __name__ == '__main__':
	RandomBot()