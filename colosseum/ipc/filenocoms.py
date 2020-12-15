import os
import sys

from .communication import CommunicationManager, ProcessDiedException

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
		
		self._read = os.fdopen(read_fileno, 'r')
		self._write = os.fdopen(write_fileno, 'w')
	
	def _close(self):
		self._read.close()
		self._write.close()
	
	def _send_str(self, msg:str):
		self._write.write(msg)
		self._write.flush()
	
	def _recv_str(self)->str:
		while True:
			msg = self._read.readline()
			if msg:
				return msg
			else:
				raise ProcessDiedException