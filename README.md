# newrelic-cgminer
[![Build Status](https://travis-ci.org/2ndalpha/newrelic-cgminer.png?branch=master)](https://travis-ci.org/2ndalpha/newrelic-cgminer)

newrelic-cgminer is New Relic plugin for monitoring CGMiner boxes.

It listens for CGMiner statistics like hashrate, reject percentage, temperature and sends it to New Relic where you can keep an eye on all of your miners.

## Installation

Currently newrelic-cgminer works only with Python 2.6 or 2.7 in Linux. Windows support will be added in the future.

1. Create a [New Relic](https://www.newrelic.com) account (It's free!)
2. Fetch licence key from New Relic account settings page
3. In your miner box run `git clone https://github.com/2ndalpha/newrelic-cgminer.git`
4. Navigate to newrelic-cgminer folder and run `pip install -r requirements.txt` to install dependencies
5. Run `python main.py <LICENCE_KEY>`
6. In few minutes "CGMiner" tab will appear in New Relic where you can see all the stats

### Running on boot
The easyest way to run newrelic-cgminer on boot-time is to add it to the crontab.
Run `crontab -e` and add
`@reboot cd <NEWRELIC_CGMINER_FOLDER> && python main.py <LICENCE_KEY>`
