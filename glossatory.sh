#!/bin/bash


ghome="/home/pi/bots/glossatory"

export PYTHONPATH="/home/pi/bots/twitterbot:$PYTHONPATH"

/usr/bin/python3.2 ${ghome}/glossatory.py  -c ${ghome}/config.yml
