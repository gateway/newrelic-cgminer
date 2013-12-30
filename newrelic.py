import logging
import json
import requests
import socket
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

__version__ = '1.0.0'

class Agent:

	PLATFORM_URL = 'https://platform-api.newrelic.com/platform/v1/metrics'
	GUID = 'com.github.2ndalpha.newrelic-cgminer'

	def __init__(self, licence_key):
		LOGGER.debug('Created New Relic Agent')
		
		self.http_headers = {'Accept': 'application/json',
                             'Content-Type': 'application/json',
                             'X-License-Key': licence_key}

		self.agent_data = {'host': socket.gethostname(),
                           'pid': os.getpid(),
                           'version': __version__}
	
		
	def send(self, metrics):
		LOGGER.debug('Sending %d metrics', len(metrics))
		
		components = list()
		components.append({'name': socket.gethostname(), 'guid':self.GUID, 'duration': 60, 'metrics':metrics})
		
		body = {'agent': self.agent_data, 'components': components}
		
		try:
			response = requests.post(self.PLATFORM_URL,
									headers=self.http_headers,
									data=json.dumps(body, ensure_ascii=False),
									verify=True)
			LOGGER.debug('Response: %s: %r',
						response.status_code,
						response.content.strip())
						
			if response.status_code == 403:
				LOGGER.error('New Relic request forbidden because of a bad licence key. Exiting.')
				sys.exit()
			if response.status_code >= 500:
				LOGGER.info('New relic did not accept the data. Trying again in 5 seconds')
				time.sleep(5)
				self.send(metrics)
				

		except requests.ConnectionError as error:
			LOGGER.error('Error reporting stats: %s', error)
