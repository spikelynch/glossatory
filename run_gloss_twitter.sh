#!/bin/bash


GLHOME="/home/mikelynch/bots_ii/glossatory"
BCHOME="/home/mikelynch/bots/botclient"

export PYTHONPATH="$BCHOME:$PYTHONPATH"
export TORCH_RNN="/home/mikelynch/torch/excavate"
export TORCH_TH="/home/mikelynch/torch/install/bin/th"
export TORCH_SCRIPT="excavate.lua"

/usr/bin/nice -n 19 /usr/local/bin/python3.5 ${GLHOME}/glossatory.py   -s Twitter -c ${GLHOME}/config/gloss_live_twitter.yml



