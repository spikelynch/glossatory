#!/bin/bash


ghome="/Users/mike/Desktop/Personal/bots/glossatory"

export PYTHONPATH="/Users/mike/Desktop/Personal/bots/botclient:$PYTHONPATH"
export TORCH_RNN="/Users/mike/torch/torch-rnn"
export TORCH_TH="/Users/mike/torch/install/bin/th"

python ${ghome}/glossatory.py -d -s Mastodon -c ${ghome}/mastodon_conf.yml
