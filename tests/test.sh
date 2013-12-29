#!/bin/bash

assert_return_code()
{
	if [ $1 != $2 ]
	then
		echo Expected return code $2. Actual code is $1.
		exit -1
	fi
}

python main.py
assert_return_code $? 2

exit 0