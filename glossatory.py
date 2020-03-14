#!/usr/bin/env python

from rnnbot import RnnBot
import time, math, random, os, os.path, re, sys, shutil

DEFAULT_COLON = ': '

class Glossatory(RnnBot):

    def configure(self):
        super(Glossatory, self).configure()
        if 'colon' in self.cf:
            self.colon = self.cf['colon']
        else:
            self.colon = DEFAULT_COLON
  

    def parse(self, lines):
        accept_re = re.compile(self.cf['accept'])
        reject_re = re.compile(self.cf['reject'], re.IGNORECASE)
        unbalanced_re = re.compile('\([^)]+$')
        parsed = []
        for raw in lines:
            m = accept_re.match(raw)
            if m:
                word = m.group(1).upper().replace('_', ' ')
                defn = m.group(2)
                if unbalanced_re.search(defn):
                    defn += ')'
                if len(word + self.colon + defn) <= self.api.char_limit:
                    parsed.append(( word, defn ))
            else:
                print("No match: {}".format(raw))
        return parsed

    def render(self, line):
        return line[0] + self.colon + line[1], line[0]



        
if __name__ == '__main__':
    g = Glossatory()
    g.run()
    # g.configure()
    # if 'colon' in g.cf:
    #     g.colon = g.cf['colon']
    # else:
    #     g.colon = DEFAULT_COLON
    # if 'spectrum' in g.cf:
    #     g.spectrum()
    # else:
    #     defn = None
    #     t = g.temperature()
    #     post, title = g.generate(t)
    #     options = {}
    #     if post:
    #         if 'content_warning' in g.cf:
    #             options['spoiler_text'] = g.cf['content_warning'].format(title)
    #         g.post(post, options)
    #     else:
    #         print("Something went wrong")

