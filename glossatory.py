#!/usr/bin/env python

from twitterbot import TwitterBot
import torchrnn


class Glossatory(TwitterBot):

    def glossolalia(self):
        return torchrnn.generate_lines(model=self.cf['model'])
        
        
        
if __name__ == '__main__':
    g = Glossatory()
    g.configure()
    tweet = g.glossolalia()
    if tweet:
        bot.post(tweet)
    else:
        print("Something went wrong")

