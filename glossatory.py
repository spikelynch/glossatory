#!/usr/bin/env python

from twitterbot import TwitterBot
import torchrnn
import time, random


class Glossatory(TwitterBot):

    def glossolalia(self):
        lines = torchrnn.generate_lines(temperature=self.cf['temperature'], model=self.cf['model'])
        return lines[0]

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

