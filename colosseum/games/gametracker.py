from abc import ABC, abstractmethod

class GameTracker(ABC):
	def __init__(self, n_players, points=None):
		self._n_players = n_players
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