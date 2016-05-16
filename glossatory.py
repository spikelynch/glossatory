#!/usr/bin/env python

from twitterbot import TwitterBot
import torchrnn


class Glossatory(TwitterBot):

    def glossolalia(self):
        lines = torchrnn.generate_lines(temperature=self.cf['temperature'], model=self.cf['model'])
        return lines[0]
        
        
if __name__ == '__main__':
    g = Glossatory()
    g.configure()
    tweet = g.glossolalia()
    if tweet:
        g.post(tweet)
    else:
        print("Something went wrong")

