from . import GTNTracker
from ..game import Bot

class Linear(Bot):
	def __init__(self):
		super().__init__(GTNTracker)
	
	def take_turn(self):
		return self.game.lower
	
	def new_game(self):
		pass

if __name__ == '__main__':
	Linear()