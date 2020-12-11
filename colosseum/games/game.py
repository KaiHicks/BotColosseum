import json
import os
import random
import sys
from abc import ABC, abstractmethod
from typing import List

class GameClient(ABC):
	"""
	Handles host-bot communications.
	"""
	def __init__(self, bot_module:str):
		"""
		params:
			bot_module:str - A string representing the arguments to pass to the
				interpreter call. 
				i.e. `python3 -m <bot_module>`
		"""
		self._points = 0
		self._bot_module = bot_module
		
		parent_read, child_write = os.pipe()
		child_read, parent_write = os.pipe()
		pid = os.fork()
		
		if pid:
			# We are the parent
			self._is_parent = True
			os.close(child_write)
			os.close(child_read)
			self._read = os.fdopen(parent_read, 'r', 1)
			self._write = parent_write
		else:
			# We are the child
			self._is_parent = False
			os.close(parent_read)
			os.close(parent_write)
			
			os.dup2(child_read, sys.stdin.fileno())
			os.dup2(child_write, sys.stdout.fileno())
			
			os.execlp('python3', 'Bot', '-m', self._bot_module)
	
	def _send(self, msg):
		"""
		Send msg to the bot
		"""
		json_ = json.dumps(msg)
		os.write(self._write, bytes(json_+'\n', 'UTF-8'))
	
	def _recv(self):
		"""
		Wait for and return an incoming message from the bot
		"""
		while True:
			msg = self._read.readline()
			if msg:
				response = json.loads(msg[:-1])
				return response
	
	def _kill_child(self):
		"""
		Kill the bot process
		"""
		self._send({'stop': {}})
	
	def take_turn(self)->dict:
		"""
		Signal the bot to take their turn and return their response
		"""
		self._send({'your_turn': {}})
		return self._recv()
	
	def update(self, *args, **kwargs):
		"""
		Update the bot to a new gamestate. Called when a bot makes their move. 
		"""
		self._send({'update': kwargs})
	
	def new_game(self, game_params):
		"""
		Signal the bot that a new game has started. 
		"""
		self._send({
			'new_game': game_params,
		})

class GameTracker(ABC):
	def __init__(self, n_players, points=None):
		self.points = points or [0 for _ in range(n_players)]
	
	@abstractmethod
	def make_move(self, *args, **kwargs)->dict:
		...
	
	@abstractmethod
	def update(self, *args, **kwargs):
		"""
		Handle gamestate updates
		"""
		...
	
	@property
	@abstractmethod
	def is_done(self):
		...

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