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
                        time.sleep(15)
                except miner.UnavailableException:
                        LOGGER.warn('CGminer is not available. Waiting 15 seconds')
                        time.sleep(15)


def print_general_info():
        version_container = cgminer.send_command('version')[0]
        if 'CGMiner' in version_container:
                LOGGER.info('cgminer v %s', version_container['CGMiner'])
        elif 'SGMiner' in version_container:
                LOGGER.info('sgminer v %s', version_container['SGMiner'])

        devices = cgminer.send_command('devdetails')
        for device in devices:
                name = device['Name']
                id = device['ID']
                driver = device['Driver']
                LOGGER.info('%s#%d: %s', name, id, driver)


def process():
        devices = cgminer.send_command('devs')
        #print devices
        metrics = {}
        max_temperature = 0

        for device in devices:
                #print device
                asc_id = device['ASC']
                temperature = device['Temperature']
                if temperature > max_temperature:
                        max_temperature = temperature
                if device['Enabled'] == 'Y':
                        #metrics["Component/FanSpeed/ASC#%d" % (asc_id)] = device['Temperature']
                        #metrics["Component/FanSpeedPercentage/ASC#%d" % (asc_id)] = device['Fan Percent']
                        metrics["Component/Temperature/ASC#%d" % (asc_id)] = device['Temperature']
                        metrics["Component/MHS/ASC#%d" % (asc_id)] = device['MHS 5s']

                        metrics["Component/RejectedPercentage/ASC#%d" % (asc_id)] = device['Device Rejected%']
                        metrics["Component/HardwareErrors/ASC#%d" % (asc_id)] = device['Hardware Errors']
                        #metrics["Component/Memory/ASC#%d" % (asc_id)] = device['Memory Clock']
                        #metrics["Component/Voltage/ASC#%d" % (asc_id)] = device['ASC Voltage']
                        #metrics["Component/Clock/ASC#%d" % (asc_id)] = device['ASC Clock']

        metrics['Component/MaxTemperature'] = max_temperature
        fill_summary_metrics(metrics)
        fill_coin_metrics(metrics)
        new_relic.send(metrics)


parser = argparse.ArgumentParser(description='Sends CGminer status to New Relic')
parser.add_argument('licence_key', help='New Relic licence key')
parser.add_argument('--cgminer_ip', dest='cgminer_ip', nargs='?', default='127.0.0.1', help='CGminer IP. Default is 127.0.0.1')
parser.add_argument('--cgminer_port', dest='cgminer_port', type=int, default=4028, help='CGminer port. Default is 4028')
parser.add_argument('--newrelic_url', dest='newrelic_url', default='https://platform-api.newrelic.com/platform/v1/metrics', help='New Relic API url')
parser.add_argument('--verbose', dest='verbose', action='store_true', help='Prints debugging information')

args = parser.parse_args()

new_relic = newrelic.Agent(args.newrelic_url, args.licence_key, args.verbose)
cgminer = miner.Cgminer(args.cgminer_ip, args.cgminer_port, args.verbose)

try:
        run()
except KeyboardInterrupt:
        LOGGER.debug('Closing the application')

