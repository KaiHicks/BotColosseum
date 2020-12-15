from colosseum.games.game import GameTracker

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