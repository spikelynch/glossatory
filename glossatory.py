#!/usr/bin/env python

from botclient import Bot
import torchrnn
import time, math, random, os.path, re, sys

DEF_MIN = 10
DEFAULT_COLON = ': '

class Glossatory(Bot):

    def glossolalia(self, t):
        result = None
        loop = 10
        min_length = DEF_MIN
        if 'minimum' in self.cf:
            min_length = self.cf['minimum']
        while not result and loop > 0:
            lines = torchrnn.generate_lines(
                n=self.cf['sample'],
                temperature=t,
                model=self.cf['model'],
                max_length=self.api.char_limit,
                min_length=min_length
                )
            lines = self.clean_glosses(lines)
            if 'logs' in self.cf:
                log = self.logfile(t)
                print("Log = {}".format(log))
                with open(log, 'wt') as f:
                    for w, d in lines:
                        f.write(w + ': ' + d)
                        f.write("\nt = {}\n".format(t))
            if len(lines) > 5:
                result = random.choice(lines[2:-2])
                loop = loop - 1
            else:
                print("Empty result set")
        return result

    def clean_glosses(self, lines):
        accept_re = re.compile(self.cf['accept'])
        reject_re = re.compile(self.cf['reject'], re.IGNORECASE)
        unbalanced_re = re.compile('\([^)]+$')
        if 'colon' in self.cf:
            self.colon = self.cf['colon']
        else:
            self.colon = DEFAULT_COLON
        cleaned = []
        for raw in lines:
            if not reject_re.match(raw):
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
        
    def random_pause(self):
        if 'pause' in self.cf:
            pause = random.randrange(0, int(self.cf['pause']))
            print("Waiting for {}".format(pause))
            time.sleep(pause)

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

    def logfile(self, t):
        if 'spectrum' in self.cf:
            return os.path.join(self.cf['logs'], self.tstamp + '.' + str(t) + '.log')
        else:
            return os.path.join(self.cf['logs'], str(time.time())) + '.log'
        
if __name__ == '__main__':
    g = Glossatory()
    g.configure()
    if 'spectrum' in g.cf:
        g.spectrum()
    else:
        t = g.sine_temp()
        defn = g.glossolalia(t)
        g.random_pause()
        options = {}
        if defn:
            if 'content_warning' in g.cf:
                options['spoiler_text'] = g.cf['content_warning'].format(defn[0])
            g.post(defn[0] + g.colon + defn[1], options)
        else:
            print("Something went wrong")

