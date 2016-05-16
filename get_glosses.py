#!/usr/bin/env python

import torchrnn, argparse

MODEL = '/Users/mike/torch/torch-rnn/cv_glossatory/checkpoint_215100.t7'


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-m', '--model', type=str, default=MODEL, help="torch-rnn checkpoint")
    ap.add_argument('-t', '--temperature', type=float, default=0.8, help="sample temperature")
    ap.add_argument('-n', '--number', type=int, default=10, help="number of tweets to sample")
    args = ap.parse_args()
    tweets = torchrnn.generate_lines(temperature=args.temperature, model=args.model, n=args.number)
    for tweet in tweets:
        print(tweet)
