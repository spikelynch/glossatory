#!/usr/bin/env python

from rnnbot import RnnBot
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import torchrnn
import re, random

DEF_MIN = 10
DEFAULT_COLON = ': '
DEFAULT_FILTER = 'filtered'

# Note: extract a list of Latin abbreviations and feed them to punkt

class AnatomyOfMelancholy(RnnBot):

    def tokenise(self, sample):
        # first pass - look for poems
        verses = self.scan_for_verse(sample)
        if verses:
            self.notes.append("got {} verses".format(len(verses)))
            return verses
        # second pass - look for sentences
        text = re.sub(r'\[\d+\]', '', sample)
        text = re.sub("\r\n", ' ', text)
        punkt_param = PunktParameters()
        punkt_param.abbrev_types = set(self.cf['abbreviations'])
        tokenizer = PunktSentenceTokenizer(punkt_param)
        sents = tokenizer.tokenize(text)
        sents = sents[1:-1]
        self.notes.append("got {} sentences".format(len(sents)))
        return sents[1:-1]

    # this assumes that the input has line breaks and has
    # not had its page numbers stripped out

    def scan_for_verse(self, sample):
        verses = []
        verse = ''
        gap = 0
        vsample = sample.replace("\r", '')
        for line in vsample.split("\n"):
            m = re.match(r'(\[\d+\])?(\s{1,8})(\S.+)$', line)
            if m:
                # if m[1]:
                #     indent = ' '* len(m[1])
                # else:
                #     indent = ''
                line = m[3]
                if gap > 0:
                    if gap > 1 or len(verse + line) > int(self.cf["min_length"]):
                        verses.append(verse)
                        verse = ''
                    verse += line + '\n'
                    gap = 0
                else:
                    verse += line + '\n'
            else:
                if re.match(r'^\s*$', line):
                    if gap == 0 and verse:
                        verse += line + '\n'
                    gap += 1
        if verse:
            verses.append(verse)
        verses = [ re.sub(r'\n+$', '', v) for v in verses ]
        return verses


    def parse(self, lines):
        cleaned = []
        for raw in lines:
            if "min_length" in self.cf:
                if len(raw) >= int(self.cf["min_length"]):
                    cleaned.append(raw)
            else:
                cleaned.append(raw)
        return cleaned

    def select(self, lines):
        if lines:
            return random.choice(lines)
        else:
            return None


if __name__ == '__main__':
    aom = AnatomyOfMelancholy()
    aom.run()




