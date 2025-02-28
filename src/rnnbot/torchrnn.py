#!/usr/bin/env python

# this needs to be updated to use docker (permissions?) and probably 
# moved into rnnbot

import subprocess
import os
import signal
import sys


SAMPLE_SIZE = 5
DEFAULT_LINE = 140
DEFAULT_LENGTH = 2000
DEFAULT_MAXTIME = 60 * 60


class TorchRNN():

    def __init__(self, cmd, model):
        self.cmd = cmd.split()
        self.model = model


    def generate_lines(self, temperature=1.0, n=1, min_length=1, max_length=DEFAULT_LINE, opts={}):
        lines = []
        while len(lines) < n:
            text = self.run_sample(temperature, '', max_length * SAMPLE_SIZE, opts).decode('utf-8')
            ls = text.split('\n')[1:]
            for l in ls:
                if not l or len(l) > max_length or len(l) < min_length:
                    continue
                lines.append(l)
        return lines[:n]

    def generate_text(self, temperature=1.0, length=DEFAULT_LENGTH, opts={}):
        return self.run_sample(temperature, '', length, opts).decode('utf-8')


    def run_sample(self, temperature, start, nchars, opts):
        cmd = self.cmd[:]
        args = {}
        args['-checkpoint'] = self.model
        args['-temperature'] = str(temperature)
        args['-length'] = str(nchars)
        args['-start_text'] = start
        if opts:
            for k, v in opts.items():
                cmd.append('--' + k)
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
        try:
            p = subprocess.Popen(
                cmd,
                cwd=TORCHRNN,
                start_new_session=True,
                stdout=subprocess.PIPE
            )
            data, err = p.communicate(timeout=DEFAULT_MAXTIME)
            return data
        except subprocess.TimeoutExpired:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
        return ""
