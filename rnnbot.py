#!/usr/bin/env python

from botclient import Bot
import torchrnn
import time, math, random, os, os.path, re, sys, shutil

DEF_MIN = 10
DEFAULT_FILTER = 'filtered'

class RnnBot(Bot):

    # Uses the torcrnn library to run the RNN, clean and log the output,
    # and return a result

    def generate(self, t):
        result = None
        loop = 10
        min_length = DEF_MIN
        if 'minimum' in self.cf:
            min_length = self.cf['minimum']
        options = {}
        if 'suppress' in self.cf:
            options['suppress'] = self.lipogram()
        else:
            self.forbid = None
        while not result and loop > 0:
            sample = torchrnn.generate_lines(
                n=self.cf['sample'],
                temperature=t,
                model=self.cf['model'],
                max_length=self.api.char_limit,
                min_length=min_length,
                opts=options
                )
            lines = self.tokenise(sample)
            lines = self.clean(lines)
            lines = self.parse(lines)
            print(lines)
            self.write_logs(t, lines)
            if len(lines) > 5:
                result = random.choice(lines[1:-2])
                loop = loop - 1
            else:
                print("Empty result set")        
        return self.render(result)

    # override this method if the RNN needs a more complicated way
    # to 

    def tokenise(self, sample):
        return sample

    # applies the accept and reject regexps

    def clean(self, lines):
        accept_re = re.compile(self.cf['accept'])
        reject_re = re.compile(self.cf['reject'], re.IGNORECASE)
        unbalanced_re = re.compile('\([^)]+$')
        cleaned = []
        for raw in lines:
            if not reject_re.search(raw):
                m = accept_re.match(raw)
                if m:
                    cleaned.append(raw)
        return cleaned

    # parse is for model-specific processing

    def parse(self, lines):
        return lines

    # render takes an individual line (which could be a string, or a
    # tuple or whatever parse emits) and returns the text of a Mastodon post
    # and an abbreviated version to be injected into a content warning, if 
    # required.
    # it's also called by the logger, so that the logged output is the
    # same as the post. This is all to allow this superclass to drive
    # GLOSSATORY, which pulls the raw output into WORD: definition 

    def render(self, line):
        return line, ''


  
    def extra_lipo(self, k, chars):
        if chars:
            if random.random() < k:
                c = random.choice(chars)
                return c + self.extra_lipo(k, chars.replace(c, ''))
        return ''

    def lipogram(self):
        forbid = self.cf['suppress']
        if 'suppress_maybe' in self.cf:
            k = 0.2
            if 'suppress_maybe_p' in self.cf:
                k = float(self.cf['suppress_maybe_p'])
            forbid += self.extra_lipo(k, self.cf['suppress_maybe'])
        forbid += forbid.upper()
        self.forbid = forbid
        return forbid

    # Writes a complete log of all output if 'logs' is defined.
    # If 'filter' is defined, runs the output through the filter
    # and append matching lines to 'filterfile' - this is how
    # the entries for the oulipo version are built

    def write_logs(self, t, lines):
        if 'logs' in self.cf:
            log = self.logfile(str(time.time()) + '.log')
            print("Log = {}".format(log))
            with open(log, 'wt') as f:
                f.write("# temperature: {}\n".format(t))
                if self.forbid:
                    f.write("# forbid: {}\n".format(self.forbid))
                for l in lines:
                    r, t = self.render(l)
                    f.write(r + "\n")
        if 'filter' in self.cf:
            fre = re.compile(self.cf['filter'])
            filterf = self.logfile(DEFAULT_FILTER)
            if 'filterfile' in self.cf:
                filterf = self.cf['filterfile']
            print("Filtered = {}".format(filterf))
            with open(filterf, 'a') as f:
                for l in lines:
                    l1, t = self.render(l)
                    if fre.match(l1):
                        f.write(l1 + "\n")
         

    # Filters the glosses for basic syntax, prohibited terms (this
    # is for racist language, not the oulipo version, see the write_logs
    # function for how that works) and unbalanced parentheses

    def clean_glosses(self, lines):
        accept_re = re.compile(self.cf['accept'])
        reject_re = re.compile(self.cf['reject'], re.IGNORECASE)
        unbalanced_re = re.compile('\([^)]+$')
        cleaned = []
        for raw in lines:
            if not reject_re.search(raw):
                m = accept_re.match(raw)
                if m:
                    word = m.group(1).upper().replace('_', ' ')
                    defn = m.group(2)
                    if unbalanced_re.search(defn):
                        defn += ')'
                    if len(word + self.colon + defn) <= self.api.char_limit:
                        cleaned.append(( word, defn ))
                else:
                    print("No match: {}".format(raw))
        return cleaned

    def sine_temp(self):
        p = float(self.cf['t_period']) * 60.0 * 60.0
        v = math.sin(time.time() / p)
        return self.cf['t_0'] + v * self.cf['t_amp']

    def rand_temp(self):
        t0 = self.cf['t_0']
        tamp = self.cf['t_amp']
        return t0 - tamp + 2 * random.random() * tamp

    def temperature(self):
        if 't_period' in self.cf:
            return self.sine_temp()
        else:
            return self.rand_temp() 
        

    def spectrum(self):
        sv = self.cf['spectrum'].split()
        self.tstamp = str(time.time())
        low = float(sv[0])
        high = float(sv[1])
        steps = int(sv[2])
        for i in range(steps):
            t = low + (high - low) * (i / (steps - 1))
            tweet = g.glossolalia(t)
            print("{}: {}".format(t, tweet))

    def logfile(self, p):
        return os.path.join(self.cf['logs'], p)
        
if __name__ == '__main__':
    rnnb = RnnBot()
    rnnb.configure()
    if 'spectrum' in rnnb.cf:
        rnnb.spectrum()
    else:
        output = None
        t = rnnb.temperature()
        output, title = rnnb.generate(t)
        options = {}
        if output:
            if 'content_warning' in rnnb.cf:
                options['spoiler_text'] = rnnb.cf['content_warning'].format(title)
            g.post(output, options)
        else:
            print("Something went wrong")

