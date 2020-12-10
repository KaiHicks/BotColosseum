import json
import os
import random
import sys
from itertools import cycle
from typing import List

from ..game import GameClient, GameTracker, GameHoster

class GTNTracker(GameTracker):
	def __init__(self, upper, lower=0):
		self._upper = upper
		self._lower = lower
		self._is_done = False
	
	def update(self, guess:int, higher:bool, correct:bool):
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
		return self._upper
	
	@property
	def lower(self):
		return self._lower
	
	@property
	def is_done(self):
		return self._is_done

class GTNHoster(GameHoster):
	def play(self, upper, lower=0):
		game = GTNTracker(upper, lower)
		secret_num = random.randint(lower, upper)
		
		for p in self._players:
			p.new_game({'lower': lower, 'upper': upper})
		
		for i, p in cycle(enumerate(self._players)):
			guess = p.take_turn()
			higher = guess < secret_num
			correct = guess == secret_num
			
			game.update(guess, higher, correct)
			self._broadcast(guess, higher, correct)
			
			if correct:
				break
		return [0 if i == j else 1 for j, p in enumerate(self._players)]
	
	def _broadcast(self, guess, higher, correct):
		for p in self._players:
			p.update(guess=guess, higher=higher, correct=correct)