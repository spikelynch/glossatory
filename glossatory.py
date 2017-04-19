#!/usr/bin/env python

from botclient import Bot
import torchrnn
import time, math, random, os.path, re

DEF_MIN = 10

class Glossatory(Bot):

    def glossolalia(self):
        result = None
        loop = 10
        t = self.sine_temp()
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
                log = os.path.join(self.cf['logs'], str(time.time())) + '.log'
                with open(log, 'wt') as f:
                    for line in lines:
                        f.write(line)
                        f.write("\n")
                        f.write("Length = {}\n\n".format(len(line)))
            print("Got {} lines on loop {}".format(len(lines), loop))
            if len(lines) > 5:
                result = random.choice(lines[2:-2])
                loop = loop - 1
        return result

    def clean_glosses(self, lines):
        accept_re = re.compile(self.cf['accept'])
        unbalanced_re = re.compile('\([^)]+$')
        cleaned = []
        for line in [ l for l in lines if accept_re.match(l) ]:
            if unbalanced_re.search(line):
                line += ')'
                if len(line) <= self.api.char_limit:
                    cleaned.append(line)
            else:
                cleaned.append(line)
        return cleaned
    
    def sine_temp(self):
        p = self.cf['t_period'] * 60.0 * 60.0
        v = math.sin(time.time() / p)
        return self.cf['t_0'] + v * self.cf['t_amp']
        
    def random_pause(self):
        if 'pause' in self.cf:
            pause = random.randrange(0, int(self.cf['pause']))
            print("Waiting for {}".format(pause))
            time.sleep(pause)

        
        
if __name__ == '__main__':
    g = Glossatory()
    g.configure()
    tweet = g.glossolalia()
    g.random_pause()
    if tweet:
        g.post(tweet)
    else:
        print("Something went wrong")

