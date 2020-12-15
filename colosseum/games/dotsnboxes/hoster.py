from .tracker import DnBTracker
from colosseum.games.game import GameHoster

class DnBHoster(GameHoster):
	def play(self, n:int=5)->DnBTracker:
		"""
		params:
			n:int=5 - Side length of the board
		returns: 
			GTNTracker - The GameTracker for this game	
		"""
		game = DnBTracker(n=n, playerid=-1)
		
		for i, p in enumerate(self._players):
			p.new_game({'playerid': i, 'n': n})
		
		while not game.is_done:
			player_id = game.whose_turn
			player = self._players[player_id]
			response = player.take_turn()
			
			# unpack response
			try:
				horizontal = response['horizontal']
				row = response['row']
				col = response['col']
				if not (isinstance(horizontal, bool) and isinstance(row, int) 
						and isinstance(col, int)):
					raise KeyError()
			except KeyError:
				game.forfeit(player_id)
				break
			game.update(player=player_id, horizontal=horizontal, row=row, 
				col=col)
			self._broadcast(player=player_id, horizontal=horizontal, row=row, 
				col=col)
		
		return game
	
	def _broadcast(self, **kwargs):
		"""
		Updates all players to the new gamestate. Called after every move. 
		"""
		for p in self._players:
			p.update(**kwargs)
