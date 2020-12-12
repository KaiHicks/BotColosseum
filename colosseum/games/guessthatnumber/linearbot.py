from colosseum.games.guessthatnumber import GTNTracker
from colosseum.games.bot import Bot

class Linear(Bot):
	def __init__(self):
		super().__init__(GTNTracker)
	
	def take_turn(self):
		return self.game.make_move(self.game.lower)
	
	def new_game(self):
		pass

if __name__ == '__main__':
	Linear()