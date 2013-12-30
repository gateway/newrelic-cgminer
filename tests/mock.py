import sys
import socket
import threading
import logging
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(format='MOCK [%(asctime)-15s] %(message)s', level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def load_data(file_name):

	data = {}
	with open (file_name, 'r') as myfile:
		lines = myfile.readlines()
		for line in lines:
			line = line.strip()
			if line.startswith('COMMAND:'):
				key = line[8:]
			if line.startswith('RESPONSE:'):
				value = line[9:]
				data[key] = value
				key = None
				value = None
				
	return data


class MockCgminer():

	def __init__(self):
		self.hostname = ''
		self.port = 4028
	

	def start(self):
		LOGGER.info('Running mock CGminer')
		backlog = 5
		size = 1024
		self.listen = True
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		s.bind((self.hostname, self.port))
		s.listen(backlog)
		while self.listen:
			client, address = s.accept() 
			if self.listen:
				request = client.recv(size)
				client.send(data_map[request])

			client.close()
			
		s.close()

	def stop(self):
		LOGGER.info('Stopping CGminer')
		self.listen = False
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.hostname, self.port))


response_codes = [500, 503, 505, 403]

class MockNewRelicRequestHandler(BaseHTTPRequestHandler):

	def do_POST(self):
		LOGGER.info('POST %s', self.path)
		
		if len(response_codes):
			code = response_codes.pop(0)
		
			self.send_response(code)
			self.end_headers()
			self.wfile.write('')
			
			if code == 403:
				self.init_shutdown()
			
		else:
			self.init_shutdown()
	
	def init_shutdown(self):
		LOGGER.info('Shutting down the New Relic mock server')
		assassin = threading.Thread(target=self.shutdown)
		assassin.daemon = True
		assassin.start()
		
	def shutdown(self):
		cgminer.stop()
		self.server.shutdown()


def mock_newrelic():
	LOGGER.info('Running mock New Relic')
	server_address = ('127.0.0.1', 6666)
	httpd = HTTPServer(server_address, MockNewRelicRequestHandler)
	httpd.serve_forever()


def start():

	t1 = threading.Thread(target=cgminer.start)
	t1.daemon = True
	t1.start()

	t2 = threading.Thread(target=mock_newrelic)
	t2.daemon = True
	t2.start()

	t1.join()
	t2.join()

file_name = sys.argv[1]
LOGGER.info('File: %s', file_name)
data_map = load_data(file_name)

cgminer = MockCgminer()
start()
