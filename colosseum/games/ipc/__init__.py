import json
import os
import signal
import sys
from abc import ABC, abstractmethod
from numbers import Number
from typing import Dict, Callable

class TimeoutException(Exception):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

def _timeout(signum, frame):
	raise TimeoutException()
# Register the timeout
signal.signal(signal.SIGALRM, _timeout)

class CommunicationManager(ABC):
	"""
	Base class for managing parent-child communications. 
	"""
	def __init__(self, is_child:bool, timeout:Number=0, 
			commands:Dict[str, Callable]=None):
		"""
		params:
			is_child:bool - True if the current process should be treated as 
				the child process. 
			timeout:Number=0 - The default amount of time to wait for a 
				response before raising a TimeoutException
			commands:Dict[str, Callable]=None - Builtin commands. If None, the
				commands log and input will be mapped so long as is_child is 
				False. If is_child is instead True, commands will be an empty
				dictionary. 
		"""
		self._is_child = is_child
		self._timeout = timeout
		
		if not is_child:
			self._commands = {'log': self._log, 'input': self._input} \
				if commands is None else commands
		else:
			self._commands = {} if commands is None else commands
	
	def _log(self, *args, **kwargs):
		kwargs['file'] = sys.stdout
		print(*args, **kwargs)
	
	def _input(self, *args, **kwargs):
		input_ = input(*args, **kwargs)
		self.send(s=input_)
	
	def register(self, command, f):
		"""
		Register a builtin command to call the function f
		"""
		self._commands[command] = f
	
	def deregister(self, command):
		"""
		Deregister the given command
		"""
		self._commands.pop(command)
	
	def send(self, **kwargs):
		self._send_str(json.dumps(kwargs)+'\n')
	
	def recv(self, timeout:Number=None)->Dict:
		"""
		Receive a message. 
		params:
			timeout:Number=None - If specified, this will override the default
				timeout set on initialization.
		"""
		if timeout is None:
			timeout = self._timeout
		
		if timeout:
			signal.alarm(timeout)
		try:
			msg = self._recv_str()
			if not msg:
				return msg
		except TimeoutException as e:
			print(e)
			return None
		if timeout:
			signal.alarm(0)
		
		response = json.loads(msg)
		# Run any registered commands
		for c, f in self._commands.items():
			params = response.pop(c, None)
			if params is not None:
				f(
					*params.get('args', []),
					**params.get('kwargs', {})
				)
		
		if response:
			return response
		else:
			return self.recv(timeout=timeout)
	
	@abstractmethod
	def _send_str(self, msg:str):
		...
	
	@abstractmethod
	def _recv_str(self)->str:
		...

class FileNoComs(CommunicationManager):
	"""
	IPC via fileno i.e. pipes. 
	"""
	def __init__(self, is_child, read_fileno=-1, write_fileno=-1):
		super().__init__(is_child)
		
		if read_fileno == -1:
			read_fileno = sys.stdin.fileno()
		if write_fileno == -1:
			write_fileno = sys.stdout.fileno()
		
		self._read = os.fdopen(read_fileno)
		self._write = write_fileno
	
	def _send_str(self, msg:str):
		os.write(self._write, bytes(msg, 'UTF-8'))
	
	def _recv_str(self)->str:
		while True:
			msg = self._read.readline()
			if msg:
				return msg
