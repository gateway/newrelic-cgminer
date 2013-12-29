import logging
import socket
import json

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class UnavailableException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class Cgminer:

	def __init__(self, ip, port):
		LOGGER.info('CGminer IP: %s', ip)
		self.ip = ip
		
		LOGGER.info('CGminer port: %d', port)
		self.port = port
	
	
	def send_command(self, command):
		try:
			s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			s.connect((self.ip, int(self.port)))
			s.send(json.dumps({'command': command}))
		
			response = self.linesplit(s)
		except socket.error:
			raise UnavailableException('CGminer unavailable')
		
		s.close()
		
		response = response.replace('\x00', '')
		response = json.loads(response)
		return response[command.upper()]
	
		
	def linesplit(self, socket):
		buffer_size = 4096
		data = socket.recv(buffer_size)
		while True:
			more = socket.recv(buffer_size)
			if not more:
				return data
			else:
				data = data+more
