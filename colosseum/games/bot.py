import sys
from abc import ABC, abstractmethod
from typing import Callable, Dict

from colosseum.ipc import FileNoComs

pipeout_fileno = sys.stdout.fileno()
pipein_fileno = sys.stdin.fileno()

_coms = FileNoComs(
	True,
	read_fileno=pipein_fileno,
	write_fileno=pipeout_fileno
)

def log(*args, **kwargs):
	"""
	Logs a message to the parent process stdout. The standard print function 
	will not work because stdout is used for inter-process communication.
	
	The parent process will only service the request when it expects a message
	from this process. I.e. during this bot's turn. 
	"""
	_coms.send(log={'args': args, 'kwargs': kwargs})

def get_input(*args, **kwargs):
	"""
	Gets an input from the parent process stdin. The standard input function 
	will not work because stdin is used for inter-process communication. 
	
	The parent process will only service the request when it expects a message
	from this process. I.e. during this bot's turn. 
	"""
	_coms.send(input={'args': args, 'kwargs':kwargs})
	response = _coms.recv()
	return response.get('s', '')

class Bot(ABC):
	"""
	Base class for a bot. 
	"""
	def __init__(self, tracker_type:type):
		"""
		params:
			tracker_type:type - The type of the associated GameTracker
		"""
		self._tracker_type = tracker_type
		
		self._commands = {'stop': self._stop, 'new_game': self._new_game, 
			'update': self._update, 'your_turn': self._take_turn}
		
		while(True):
			msg = _coms.recv()
			for command, params in msg.items():
				# I cannot use the walrus operator since this might run on 
				# earlier versions of python
				target = self._commands.get(command, None)
				if target is not None:
					target(**params)
	
	def _register_commands(self, commands:Dict[str, Callable]):
		self._commands.update(commands)
	
	def _register_command(self, command:str, target:Callable):
		self._register_commands({command: target})
	
	def _stop(self, **kwargs):
		_coms.close()
		exit(kwargs.get('eid', 0))
	
	def _update(self, **kwargs):
		self._game.update(**kwargs)
		self.update()
	
	def _take_turn(self, **kwargs):
		response = self.take_turn()
		_coms.send(**response)
	
	def _new_game(self, **game_params):
		self._game = self._tracker_type(**game_params)
		self.new_game()
	
	@property
	def game(self):
		return self._game
	
	@abstractmethod
	def take_turn(self):
		"""
		The logic for the bot to take their turn
		returns:
			The move that the bot wishes to make
		"""
		...
	
	@abstractmethod
	def update(self):
		...
	
	@abstractmethod
	def new_game(self):
		"""
		A 'reset' method to start a new game. This does not have to reset the 
		bot to its original state. The reason to use a resetter over 
		re-instantiating or re-initializing the object is to allow for 
		'remembering' behavior. 
		"""
		...