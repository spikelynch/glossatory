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
        text = re.sub(r'\[\d+\]', '', sample)
        text = re.sub("\r\n", ' ', text)
        punkt_param = PunktParameters()
        punkt_param.abbrev_types = set(self.cf['abbreviations'])
        tokenizer = PunktSentenceTokenizer(punkt_param)
        sents = tokenizer.tokenize(text)
        return sents[1:-1]

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
        return random.choice(lines)


if __name__ == '__main__':
    aom = AnatomyOfMelancholy()
    aom.run()




