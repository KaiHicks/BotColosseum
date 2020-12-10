import json
import os
import random
import sys
from abc import ABC, abstractmethod

class GameClient(ABC):
	def __init__(self, bot_module):
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
			self._read = os.fdopen(child_read, 'r', 1)
			
			os.dup2(child_read, sys.stdin.fileno())
			os.dup2(child_write, sys.stdout.fileno())
			
			os.execlp('python3', 'Bot', '-m', self._bot_module)
	
	def _send(self, msg):
		json_ = json.dumps(msg)
		os.write(self._write, bytes(json_+'\n', 'UTF-8'))
	
	def _recv(self):
		while True:
			msg = self._read.readline()
			if msg:
				response = json.loads(msg[:-1])
				return response
	
	def _kill_child(self):
		self._send({'stop': True})
	
	def take_turn(self):
		self._send({'your_turn': True})
		return self._recv()['guess']
	
	def update(self, **kwargs):
		self._send({'update': kwargs})
	
	def new_game(self, game_params):
		self._send({
			'new_game': True,
			'game_params': game_params
		})

class GameTracker(ABC):
	@abstractmethod
	def update(self, *args, **kwargs):
		...
	
	@property
	@abstractmethod
	def is_done(self):
		...

class GameHoster(ABC):
	def __init__(self, player_modules, shuffle_players=True):
		self._players = ShuffledList(GameClient(pm)
			for pm in player_modules)
		self._total_points = [0 for p in self._players]
		self._shuffle_players = shuffle_players
		self._n_games = 0
	
	def start_game(self, *args, **kwargs):
		if self._shuffle_players:
			self._players.shuffle
		points = self.play(*args, **kwargs)
		
		points = ShuffledList(points, self._players.mapping)
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
	def play(self, *args, **kwargs):
		...

class Bot(ABC):
	def __init__(self, tracker_type):
		self._read = os.fdopen(sys.stdin.fileno(), 'r')
		self._write = sys.stdout.fileno()
		self._tracker_type = tracker_type
		
		while(True):
			msg = self._recv()
			if msg.get('stop', False):
				exit()
			elif msg.get('new_game', False):
				game_params = msg.get('game_params', False)
				if not game_params:
					raise Exception(
						'New game requested but no game parameters given'
					)
				
				self._new_game(game_params)
			else:
				update = msg.get('update', {})
				if update:
					self._game.update(**update)
				if msg.get('your_turn', False):
					guess = self.take_turn()
					self._send(guess=guess)
	
	def _send(self, **kwargs):
		json_out = json.dumps(kwargs)
		os.write(self._write, bytes(json_out+'\n', 'UTF-8'))
	
	def _recv(self):
		while True:
			msg = self._read.readline()
			if msg:
				response = json.loads(msg[:-1])
				return response
	
	def _new_game(self, game_params):
		self._game = self._tracker_type(**game_params)
		self.new_game()
	
	@property
	def game(self):
		return self._game
	
	@abstractmethod
	def take_turn(self):
		...
	
	@abstractmethod
	def new_game(self):
		...

class ShuffledList:
	def __init__(self, items, mapping=None):
		self._items = list(items)
		self._mapping = mapping or list(range(len(self._items)))
	
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
		self._mapping = list(range(len(self._items)))
	
	def __str__(self):
		return str(self._items)