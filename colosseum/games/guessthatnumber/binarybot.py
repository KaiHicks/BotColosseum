from . import GTNTracker
from ..game import Bot

class BinSearch(Bot):
	def __init__(self):
		super().__init__(GTNTracker)
	
	def take_turn(self):
		return self.game.lower + (self.game.upper - self.game.lower)//2
	
	def new_game(self):
		pass

if __name__ == '__main__':
	BinSearch()