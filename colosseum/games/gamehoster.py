import random
from abc import ABC, abstractmethod
from typing import List

from .gameclient import GameClient
from .gametracker import GameTracker

class GameHoster(ABC):
	"""
	Hosts a game and manages the bots.
	"""
	def __init__(self, player_modules:List[str], shuffle_players=True):
		"""
		params:
			player_modules:List[str] - A list of strings representing the 
				arguments to pass to the interpreter calls. 
				i.e. `python3 -m <bot_module>`
			shuffle_players=True - If True, the player order will be shuffled 
				every time a new game is started. 
		"""
		self._players = ShuffledList(GameClient(pm)
			for pm in player_modules)
		self._total_points = [0 for p in self._players]
		self._shuffle_players = shuffle_players
		self._n_games = 0
	
	def start_game(self, *args, **kwargs):
		if self._shuffle_players:
			self._players.shuffle
		tracker = self.play(*args, **kwargs)
		
		points = ShuffledList(tracker.points, self._players.mapping)
		self._players.unshuffle
		points.unshuffle
		for i, s in enumerate(points):
			self._total_points[i] += s
		
		self._n_games += 1
	
	@property
	def n_games(self):
		return self._n_games
	
	@property
	def total_points(self):
		return self._total_points
	
	@property
	def avg_points(self):
		return [s/self._n_games for s in self._total_points]
	
	@abstractmethod
	def play(self, *args, **kwargs)->GameTracker:
		...

class ShuffledList:
	"""
	An easily shufflable list that remembers the original order.
	"""
	def __init__(self, items, mapping=None):
		"""
		params:
			items:iterable - The items to populate the list
			mappting:iterable=None - The default ordering of the list. Must 
				contain every integer from zero to len(items)-1 exactly once. 
		"""
		self._items = list(items)
		self._mapping = mapping or list(range(len(self._items)))
	
	def __len__(self):
		return len(self._items)
	
	def __getitem__(self, i):
		return self._items[self._mapping[i]]
	
	def __setitem(self, i, x):
		self._items[self._mapping[i]] = x
	
	def __iter__(self):
		for i in self._mapping:
			yield self._items[i]
	
	@property
	def mapping(self):
		return self._mapping
	
	def shuffle(self):
		random.shuffle(self._mapping)
	
	def unshuffle(self):
		"""
		Revert the list back to its original state. 
		"""
		self._mapping = list(range(len(self._items)))
	
	def __str__(self):
		return str(self._items)