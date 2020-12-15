import os
import sys
from abc import ABC

from colosseum.ipc import FileNoComs

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
			
			self._coms = FileNoComs(
				False,
				read_fileno=parent_read,
				write_fileno=parent_write
			)
		else:
			# We are the child
			self._is_parent = False
			os.close(parent_read)
			os.close(parent_write)
			
			os.dup2(child_read, sys.stdin.fileno())
			os.dup2(child_write, sys.stdout.fileno())
			
			os.execlp('python3', 'Bot', '-m', self._bot_module)
	
	def _kill_child(self):
		"""
		Kill the bot process and close the communication. 
		"""
		self._coms.send(**{'stop': {}})
		self._coms.close()
	
	def take_turn(self)->dict:
		"""
		Signal the bot to take their turn and return their response
		"""
		self._coms.send(**{'your_turn': {}})
		return self._coms.recv()
	
	def update(self, *args, **kwargs):
		"""
		Update the bot to a new gamestate. Called when a bot makes their move. 
		"""
		self._coms.send(**{'update': kwargs})
	
	def new_game(self, game_params):
		"""
		Signal the bot that a new game has started. 
		"""
		self._coms.send(new_game=game_params)
	
	def __del__(self):
		self._kill_child()