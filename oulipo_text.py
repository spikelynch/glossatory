#!/usr/bin/env python

from botclient.textbot import TextBot
import re

DEFAULT_COLON = ': '

class OulipoGlossatory(TextBot):

    # calls TextBot's get_next, then splits the result into
    # a term and definition

    def get_next(self):
        try:
            line = super(OulipoGlossatory, self).get_next()
            filter = self.cf['filter']
            oulipo_re = re.compile(filter)
            m = oulipo_re.match(line)
            if m:
                return ( m.group(1), m.group(2) )
            else:
                return None
        except Exception as e:
            print("Ran out of lines")
            return None


if __name__ == '__main__':
    og = OulipoGlossatory()
    og.configure()
    if 'colon' in og.cf:
        og.colon = og.cf['colon']
    else:
        og.colon = DEFAULT_COLON
    defn = og.get_next()
    if defn:
        options = {}
        if 'content_warning' in og.cf:
            options['spoiler_text'] = og.cf['content_warning'].format(defn[0])
        og.post(defn[0] + og.colon + defn[1], options)
    else:
        print("Something went wrong")

