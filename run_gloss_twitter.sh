#!/bin/bash

GLHOME="/Users/mike/Desktop/bots_separate/glossatory"
BCHOME="/Users/mike/Desktop/bots/botclient"

export PYTHONPATH="$BCHOME:$PYTHONPATH"

export TORCH_RNN="/Users/mike/torch/torch-rnn"
export TORCH_TH="/Users/mike/torch/install/bin/th"
export TORCH_SCRIPT="excavate.lua"

export LUA_PATH="$TORCH_RNN/?.lua;$LUA_PATH"


/anaconda3/envs/bots/bin/python ${GLHOME}/glossatory.py  -d -s Twitter -c ${GLHOME}/config/gloss_live_twitter.yml


# /usr/local/bin/python3.5 ${GLHOME}/oulipo_glossatory.py -s Twitter -c ${GLHOME}/config/gloss_twitter.yml

