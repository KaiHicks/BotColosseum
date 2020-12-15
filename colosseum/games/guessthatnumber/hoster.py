import random
from itertools import cycle

from .tracker import GTNTracker
from colosseum.games import GameHoster

class GTNHoster(GameHoster):
	def play(self, upper:int, lower:int=0)->GTNTracker:
		"""
		params:
			upper:int - Exclusive upper bound of the secret number
			lower:int=0 - Inclusive lower bound of the secret number
		returns: 
			GTNTracker - The GameTracker for this game
		"""
		game = GTNTracker(len(self._players), upper, lower)
		secret_num = random.randint(lower, upper)
		
		for i, p in enumerate(self._players):
			p.new_game(
				{'playerid': i, 'n_players': len(self._players), 
				'lower': lower, 'upper': upper}
			)
		
		forfeited = set()
		for i, p in cycle(enumerate(self._players)):
			if i in forfeited:
				continue
			response = p.take_turn()
			guess = response.get('guess', None)
			if not isinstance(guess, int) or not (lower <= guess < upper):
				forfeited.add(i)
				if len(forfeited) == len(self._players):
					break
				continue
				
			higher = guess < secret_num
			correct = guess == secret_num
			
			game.update(i, guess, higher, correct)
			self._broadcast(i, guess, higher, correct)
			
			if correct:
				break
		return game
	
	def _broadcast(self, player:int, guess:int, higher:int, correct:int):
		"""
		Updates all players to the new gamestate. Called after every move. 
		params:
			player:int - The id of the player that made the guess
			guess:int - The guess the bot made
			higher:bool - If True, the true value is higher than the guess
			correct: - If True, the guess was correct
		"""
		for p in self._players:
			p.update(player=player, guess=guess, higher=higher, 
				correct=correct)