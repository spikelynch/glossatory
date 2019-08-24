#!/bin/bash


ghome="/home/pi/bots_ii/glossatory"

export PYTHONPATH="/home/pi/bots/botclient:$PYTHONPATH"
export TORCH_RNN="/home/pi/torch/torch-rnn"
export TORCH_TH="/home/pi/torch/install/bin/th"

/usr/bin/python3.2 ${ghome}/glossatory.py -s Mastodon  -c ${ghome}/vulgar_mastodon.yml
