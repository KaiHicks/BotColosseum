import os
import sys

from .communication import CommunicationManager

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
	
	def close(self):
		self._read.close()
		os.close(self._write)
	
	def _send_str(self, msg:str):
		os.write(self._write, bytes(msg, 'UTF-8'))
	
	def _recv_str(self)->str:
		while True:
			msg = self._read.readline()
			if msg:
				return msg
			else:
				self.log(f'Received blank: {msg}')