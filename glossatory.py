#!/usr/bin/env python

from twitterbot import TwitterBot
import torchrnn
import time, random, os.path


class Glossatory(TwitterBot):


    # note - filter lines to make sure that they include a definition
    # before doing the random choice.
    def glossolalia(self):
        lines = torchrnn.generate_lines(n=self.cf['sample'], temperature=self.cf['temperature'], model=self.cf['model'])
        log = os.path.join(self.cf['logs'], str(time.time())) + '.log'
        with open(log, 'wt') as f:
                for line in lines:
                        f.write(line)
                        f.write("\n")
        return random.choice(lines[2:-1])

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

