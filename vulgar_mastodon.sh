#!/bin/bash

BHOME="/Users/mike/Desktop/Personal/bots"
GHOME="$BHOME/glossatory"

# export PYTHONPATH="$BHOME/:$PYTHONPATH"
export TORCH_RNN="/Users/mike/torch/torch-rnn"
export TORCH_TH="/Users/mike/torch/install/bin/th"

python ${GHOME}/glossatory.py -s Mastodon -c vulgar_mastodon.yml 
