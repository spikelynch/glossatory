#!/usr/bin/env python

from rnnbot.rnbot import RnnBot
from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
import re, random

DEF_MIN = 10
DEFAULT_COLON = ': '
DEFAULT_FILTER = 'filtered'

SENTENCE_MATCH = 15


class AnatomyOfMelancholy(RnnBot):

    # TODO - make this collect more stuff so it works better with caching

    # problem - this now includes verses twice - once as verses, second time
    # as sentences
    #
    # need to go through the sentences and remove things which are "like"
    # the verses (though they won't be exactly the same)

    def tokenise(self, sample):
        # first pass - look for poems
        verses = self.scan_for_verse(sample)
        if verses:
            self.notes.append("got {} verses".format(len(verses)))
            verses = [ re.sub(r'\[\d+\]', '', v) for v in verses ]
        else:
            verses = []
        # second pass - look for sentences
        text = re.sub(r'\[\d+\]', '', sample)
        text = re.sub("\r\n", ' ', text)
        punkt_param = PunktParameters()
        punkt_param.abbrev_types = set(self.cf['abbreviations'])
        tokenizer = PunktSentenceTokenizer(punkt_param)
        sentences = tokenizer.tokenize(text)
        sentences = sentences[1:-1]
        self.notes.append("got {} sentences".format(len(sentences)))
        # remove any sentences which we already found as part of verses
        for s in sentences:
            matches = [ v for v in verses if s[:SENTENCE_MATCH] in v ]
            if matches:
                self.notes.append("found sentence {} in verses {}".format(s, matches))
                sentences.remove(s)
        verses.extend(sentences)
        return verses
        #return sents[1:-1]

    # this assumes that the input has line breaks and has
    # not had its page numbers stripped out

    def scan_for_verse(self, sample):
        verses = []
        verse = ''
        gap = 0
        n = 0
        vsample = sample.replace("\r", '')
        for line in vsample.split("\n"):
            m = re.match(r'(\[\d+\])?(\s{1,12})(\S.+)$', line)
            if m:
                self.notes.append("[{}] verse line {}".format(n, line[:20]))
                line = m.group(3)
                if verse and gap > 1:
                    self.notes.append("[{}] end of long gap {}".format(n, gap))
                    if verse:
                        verses.append(verse)
                    verse = ''
                elif verse and gap == 1:
                    verse += '\n'
                    self.notes.append("[{}] end of short gap {}".format(n, gap))
                verse += line + '\n'
                gap = 0
            else:
                if re.match(r'^\s*$', line):
                    self.notes.append("[{}] blank line {}".format(n, gap))
                    gap += 1
                else:
                    self.notes.append("[{}] nonverse line {} {}".format(n, gap, line[:20]))
                    if verse:
                        verses.append(verse)
                        verse = ''
                    gap = 0
            n += 1
        if verse:
            verses.append(verse)
        verses = [ re.sub(r'\n+$', '', v) for v in verses ]
        verses = [ v for v in verses if len(v.split("\n")) > 1 ]
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


    # note: select doesn't get called any more
    def select(self, lines):
        if lines:
            return random.choice(lines)
        else:
            return None


if __name__ == '__main__':
    aom = AnatomyOfMelancholy()
    aom.run()




