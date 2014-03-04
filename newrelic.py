import logging
import json
import requests
import socket
import os
import sys
import time

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

__version__ = '0.0.9'

class Agent:
        GUID = 'com.github.gateway.newrelic-cgminer'

        def __init__(self, url, licence_key, verbose):
                LOGGER.debug('Created New Relic Agent')

                self.url = url
                self.verbose = verbose
                self.http_headers = {'Accept': 'application/json',
                             'Content-Type': 'application/json',
                             'X-License-Key': licence_key}

                self.agent_data = {'host': socket.gethostname(),
                           'pid': os.getpid(),
                           'version': __version__}


        def send(self, metrics):
                LOGGER.debug('Sending %d metrics', len(metrics))

                components = list()
                components.append({'name': socket.gethostname(), 'guid':self.GUID, 'duration': 30, 'metrics':metrics})
                if self.verbose:
                        LOGGER.info(components)

                body = {'agent': self.agent_data, 'components': components}

                try:
                        response = requests.post(self.url,
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

