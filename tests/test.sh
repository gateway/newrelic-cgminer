#!/bin/bash

SCRIPT=main.py

assert_return_code()
{
	if [ $1 != $2 ]
	then
		echo Expected return code $2. Actual code is $1.
		exit -1
	fi
}

python $SCRIPT
assert_return_code $? 2

cd tests
python mock.py data1.txt &

cd ..
python $SCRIPT --newrelic_url http://localhost:6666/ fake_key

exit 0