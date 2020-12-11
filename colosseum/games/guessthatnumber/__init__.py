"""
A simple guess-that-number game. Players take turns guessing a secret number 
between lower and upper (normally 0 and 100). After a guess, all players are 
informed of the guess as well as if the secret number was lower or higher. The 
game ends when some player guesses the secret number correctly. That player is
the winner. 
"""

import random
from itertools import cycle

from ..game import GameTracker, GameHoster

class GTNTracker(GameTracker):
	def __init__(self, n_players:int, upper:int, lower:int=0, playerid:int=-1):
		super().__init__(n_players)
		"""
		params:
			n_players:int - Number of players
			upper:int - Exclusive upper bound of the secret number
			lower:int=0 - Inclusive lower bound of the secret number
			playerid:int=-1 - The id of the player that created this tracker. 
					If the tracker was created by the host, the id is -1 (default).
		"""
		self._upper = upper
		self._lower = lower
		self._is_done = False
	
	def make_move(self, guess, *args, **kwargs):
		return {'guess':guess}
	
	def update(self, player:int, guess:int, higher:bool, correct:bool):
		"""
		params:
			guess:int - The guess the bot made
			higher:bool - If True, the true value is higher than the guess
			correct:bool - If True, the guess was correct
		"""
		if correct:
			self._upper = guess
			self._lower = guess
			self.points[player] = 1
			self._is_done = True
		elif higher:
			self._lower = guess + 1
		else:
			self._upper = guess
	
	@property
	def upper(self):
		"""
		Exclusive upper bound of the secret number
		"""
		return self._upper
	
	@property
	def lower(self):
		"""
		Inclusive lower bound of the secret number
		"""
		return self._lower
	
	@property
	def is_done(self):
		return self._is_done

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
				{'playerid': i, 'n_players': len(self._players), 'lower': lower, 
				'upper': upper}
			)
		
		forfeited = set()
		for i, p in cycle(enumerate(self._players)):
			if i in forfeited:
				continue
			response = p.take_turn()
			guess = response.get('guess', None)
			if not isinstance(guess, int) or not (lower <= guess < upper):
				forfeited.add(i)
				
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
			p.update(player=player, guess=guess, higher=higher, correct=correct)