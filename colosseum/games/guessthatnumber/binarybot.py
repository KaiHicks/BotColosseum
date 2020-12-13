from colosseum.games.guessthatnumber import GTNTracker
from colosseum.games.bot import Bot

class BinSearch(Bot):
	def __init__(self):
		super().__init__(GTNTracker)
	
	def take_turn(self, **kwargs):
		guess = self.game.lower + (self.game.upper - self.game.lower)//2
		return self.game.make_move(guess)
	
	def update(self):
		pass
	
	def new_game(self, **kwargs):
		pass

if __name__ == '__main__':
	BinSearch()