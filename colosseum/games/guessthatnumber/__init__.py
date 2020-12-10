"""
A simple guess-that-number game. Players take turns guessing a secret number 
between lower and upper (normally 0 and 100). After a guess, all players are 
informed of the guess as well as if the secret number was lower or higher. The 
game ends when some player guesses the secret number correctly. That player is
the winner. 
"""

import json
import os
import random
import sys
from itertools import cycle
from typing import List

from ..game import GameClient, GameTracker, GameHoster

class GTNTracker(GameTracker):
	def __init__(self, upper:int, lower:int=0):
		self._upper = upper
		self._lower = lower
		self._is_done = False
	
	def update(self, guess:int, higher:bool, correct:bool):
		"""
		params:
			guess:int - The guess the bot made
			higher:bool - If True, the true value is higher than the guess
			correct: - If True, the guess was correct
		"""
		if correct:
			self._upper = guess
			self._lower = guess
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
	def play(self, upper:int, lower:int=0)->List[int]:
		"""
		params:
			upper:int - Exclusive upper bound of the secret number
			lower:int=0 - Inclusive lower bound of the secret number
		returns: 
			List[int] - 1 for the winning player; 0 for the rest. 
		"""
		game = GTNTracker(upper, lower)
		secret_num = random.randint(lower, upper)
		
		for p in self._players:
			p.new_game({'lower': lower, 'upper': upper})
		
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
			
			game.update(guess, higher, correct)
			self._broadcast(guess, higher, correct)
			
			if correct:
				break
		return [0 if i == j else 1 for j, p in enumerate(self._players)]
	
	def _broadcast(self, guess:int, higher:int, correct:int):
		"""
		Updates all players to the new gamestate. Called after every move. 
		params:
			guess:int - The guess the bot made
			higher:bool - If True, the true value is higher than the guess
			correct: - If True, the guess was correct
		"""
		for p in self._players:
			p.update(guess=guess, higher=higher, correct=correct)