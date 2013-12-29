import time
import logging
import argparse

import newrelic
import cgminer as miner

logging.basicConfig(format='[%(asctime)-15s] %(message)s')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def fill_summary_metrics(metrics):
	summary = cgminer.send_command('summary')[0]
	
	metrics['Component/MHS'] = summary['MHS 5s']
	metrics['Component/RejectedPercentage'] = summary['Device Rejected%']


def fill_coin_metrics(metrics):
	coins = cgminer.send_command('coin')
	
	nr = 1
	for coin in coins:
		metrics["Component/NetworkDifficulty/Coin#%d" % (nr)] = coin['Network Difficulty']
		nr = nr + 1

def run():
	while True:
		try:
			print_general_info()
			break
		except miner.UnavailableException:
			LOGGER.warn('CGminer is not available. Waiting 10 seconds')
			time.sleep(10)
	
	while True:
		try:
			process()
			time.sleep(60)
		except miner.UnavailableException:
			LOGGER.warn('CGminer is not available. Waiting 60 seconds')
			time.sleep(60)


def print_general_info():
	version = cgminer.send_command('version')[0]['CGMiner']
	LOGGER.info('cgminer v %s', version)
	
	devices = cgminer.send_command('devdetails')
	for device in devices:
		name = device['Name']
		id = device['ID']
		model = device['Model']
		LOGGER.info('%s#%d: %s', name, id, model)


def process():
	devices = cgminer.send_command('devs')
	metrics = {}
	
	for device in devices:
		gpu_id = device['GPU']
		
		metrics["Component/FanSpeed/GPU#%d" % (gpu_id)] = device['Fan Speed']
		metrics["Component/FanSpeedPercentage/GPU#%d" % (gpu_id)] = device['Fan Percent']
		metrics["Component/Temperature/GPU#%d" % (gpu_id)] = device['Temperature']
		metrics["Component/MHS/GPU#%d" % (gpu_id)] = device['MHS 5s']
		
		metrics["Component/RejectedPercentage/GPU#%d" % (gpu_id)] = device['Device Rejected%']
		
		metrics["Component/Memory/GPU#%d" % (gpu_id)] = device['Memory Clock']
		metrics["Component/Voltage/GPU#%d" % (gpu_id)] = device['GPU Voltage']
		metrics["Component/Clock/GPU#%d" % (gpu_id)] = device['GPU Clock']

	fill_summary_metrics(metrics)
	fill_coin_metrics(metrics)
	new_relic.send(metrics)
	

parser = argparse.ArgumentParser(description='Sends CGminer status to New Relic')
parser.add_argument('licence_key', help='New Relic licence key')
parser.add_argument('--cgminer_ip', dest='cgminer_ip', nargs='?', default='127.0.0.1', help='CGminer IP. Default is 127.0.0.1')
parser.add_argument('--cgminer_port', dest='cgminer_port', nargs='?', type=int, default=4028, help='CGminer port. Default is 4028')

args = parser.parse_args()

new_relic = newrelic.Agent(args.licence_key)
cgminer = miner.Cgminer(args.cgminer_ip, args.cgminer_port)

try:
	run()
except KeyboardInterrupt:
	LOGGER.debug('Closing the application')
