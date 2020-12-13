from . import GTNTracker
from ..bot import Bot, log, get_input

class Human(Bot):
	def __init__(self):
		super().__init__(GTNTracker)
	
	def take_turn(self):
		log(f'{self.game.lower} <= secretnum <= {self.game.upper-1}')
		log('Enter your guess')
		guess = int(get_input('> '))
		return self.game.make_move(guess)
	
	def update(self):
		pass
	
	def new_game(self):
		log(f'New game, {self.game.lower}-{self.game.upper-1}')

if __name__ == '__main__':
	Human()