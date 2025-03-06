#!/usr/bin/env python

import argparse
from pathlib import Path
import subprocess
import os
import signal
import sys

DOCKER_IMAGE="torchrnn"
TH="/root/torch/install/bin/th"
TORCHRNN="/root/torch-rnn"
DEFAULT_SCRIPT="sample.lua"

SAMPLE_SIZE = 5
DEFAULT_LINE = 140
DEFAULT_LENGTH = 2000
DEFAULT_MAXTIME = 60 * 60


class TorchRNN():

    def __init__(self, model_dir, model, script=DEFAULT_SCRIPT):
        self.cmd = [
            "/usr/bin/docker", "run", "-t", "--rm", 
            "--volume", f"{model_dir}:/models",
            DOCKER_IMAGE,
            TH, f"{TORCHRNN}/{script}", "-gpu", "-1",
        ]
        self.model = model


    def generate_lines(self, temperature=1.0, n=1, min_length=1, max_length=DEFAULT_LINE, sample_size=SAMPLE_SIZE, opts={}):
        lines = []
        while len(lines) < n:
            print("Sampling...")
            text = self.run_sample(temperature, '', max_length * sample_size, opts).decode('utf-8')
            ls = text.split('\n')[1:]
            for l in ls:
                if not l or len(l) > max_length or len(l) < min_length:
                    continue
                lines.append(l)
            nlines = len(lines)
            print(f"Got {nlines} lines")
            if nlines == 0:
                print(f"Raw = '{text}'")
                sys.exit(-1)
        return lines[:n]

    def generate_text(self, temperature=1.0, length=DEFAULT_LENGTH, opts={}):
        return self.run_sample(temperature, '', length, opts).decode('utf-8')


    def run_sample(self, temperature, start, nchars, opts):
        cmd = self.cmd[:]
        args = {}
        args['-checkpoint'] = f"/models/{self.model}"
        args['-temperature'] = str(temperature)
        args['-length'] = str(nchars)
        args['-start_text'] = start
        if opts:
            for k, v in opts.items():
                cmd.append('-' + k)
                cmd.append(v)
        for k, v in args.items():
            cmd.append(k)
            cmd.append(v)
        return self.run_subprocess(cmd)


    def run_subprocess(self, cmd):
        """
        Trying this method to start the lua subprocess, timeout after
        DEFAULT_MAXTIME, and then send a kill signal to it and any child processes
        if it expires.
        """
        print(cmd)
        try:
            p = subprocess.Popen(
                cmd,
                start_new_session=True,
                stdout=subprocess.PIPE
            )
            data, err = p.communicate(timeout=DEFAULT_MAXTIME)
            return data
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            print("timed out!")
        return ""

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument('-d', '--dir', type=Path)
    ap.add_argument('-m', '--model', type=str)
    ap.add_argument('-t', '--temperature', type=float, default=0.5)
    ap.add_argument('-l', '--lines', type=int, default=10)
    args = ap.parse_args()
    t = TorchRNN(args.dir, args.model)
    lines = t.generate_lines(temperature=args.temperature, n=args.lines)
    for line in lines:
        print(line)

