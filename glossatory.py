#!/usr/bin/env python

from rnnbot.rnnbot import RnnBot
import re

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
        unbalanced_re = re.compile('\([^)]+$')
        parsed = []
        for raw in lines:
            m = accept_re.match(raw)
            if m:
                word = m.group(1).upper().replace('_', ' ')
                defn = m.group(2)
                if unbalanced_re.search(defn):
                    defn += ')'
                parsed.append(( word, defn ))
            else:
                print("No match: {}".format(raw))
        return parsed

    def render(self, line):
        return line[0] + self.colon + line[1], line[0]

    def cacheparse(self, strline):
        # only split once because definitions might have colons in them
        parts = strline.split(self.colon, 1)
        return strline, parts[0]

if __name__ == '__main__':
    g = Glossatory()
    g.run()
