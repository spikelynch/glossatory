#!/bin/bash


ghome="/home/pi/bots/glossatory"

export PYTHONPATH="/home/pi/bots/twitterbot:$PYTHONPATH"
export TORCH_RNN="/home/pi/torch/torch-rnn"
export TORCH_TH="/home/pi/torch/install/bin/th"

/usr/bin/python3.2 ${ghome}/glossatory.py -c ${ghome}/config.yml
