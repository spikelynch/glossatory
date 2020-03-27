
#!/usr/bin/env python

from botclient import Bot
import torchrnn
import time, math, random, os, os.path, re, sys, shutil

DEF_MIN = 10
DEF_LOOP_MAX = 10
DEFAULT_FILTER = 'filtered'

class RnnBot(Bot):

    # Add a -t / --test flag for testing parsers

    def __init__(self):
        super().__init__()
        self.timestamp = str(time.time())
        self.ap.add_argument('-x', '--extra', action='store_true', help="Write extra debug output to logs")
        self.ap.add_argument('-t', '--test', action='store_true', help="Test parser on RNN output")
        self.ap.add_argument('-p', '--pregen', default=None, help="Test parser on pre-generated output (file or directory)")



    def prepare(self, t):
        self.temperature = t
        self.notes = []
        self.min_length = DEF_MIN
        if 'min_length' in self.cf:
            self.min_length = int(self.cf['min_length'])
        self.max_length = self.api.char_limit
        if 'max_length' in self.cf:
            self.max_length = int(self.cf['max_length'])
        self.loop_max = DEF_LOOP_MAX
        if 'loop' in self.cf:
            self.loop_max = int(self.cf['loop'])
        if 'minimum' in self.cf:
            self.min_length = self.cf['minimum']
        if 'sample_method' in self.cf and self.cf['sample_method'] == 'text':
            self.log_sep = "\n---\n" 
        else:
            self.log_sep = "\n" 
        self.options = {}
        if 'suppress' in self.cf:
            self.options['suppress'] = self.lipogram()
        else:
            self.forbid = None

    def sample(self):
        if 'sample_method' in self.cf and self.cf['sample_method'] == 'text':
            print("Sampling using text")
            self.raw_rnn = torchrnn.generate_text(
                temperature=self.temperature,
                model=self.cf['model'],
                length=self.cf['sample'],
                opts=self.options
            )
        else:
            self.raw_rnn = torchrnn.generate_lines(
                n=self.cf['sample'],
                temperature=self.temperature,
                model=self.cf['model'],
                max_length=self.max_length,
                min_length=self.min_length,
                opts=self.options
            )

        return self.raw_rnn



    # Uses the torcrnn library to run the RNN, clean and log the output,
    # and return a result

    def generate(self, t):
        result = None
        self.loop = 0
        self.prepare(t)
        while not result and self.loop < self.loop_max:
            self.notes.append("Pass {}".format(self.loop))
            sample = self.sample()
            lines = self.process(sample)
            self.write_logs(t, lines)
            result = self.select(lines)
            self.loop = self.loop + 1
        self.notes.append("Result: '{}'".format(result))
        if self.notes:
            self.write_debug(self.notes, '6.notes.txt')
        return self.render(result)

    # Used in test mode: collects one batch and renders all of them

    def test(self, t):
        self.prepare(t)
        sample = self.sample()
        lines = self.process(sample)
        if self.notes:
            self.write_debug(self.notes, '6.notes.txt')
        for output, title in [ self.render(l) for l in lines ]:
            print(output + "\n--\n")

    def pregen(self):
        files = self.get_pregen()
        for f in files:
            with open(f, 'r') as fh:
                print("# {}\n".format(f))
                rawlines = fh.read()
                sample = rawlines.replace("\n", " ")
                lines = self.process(sample)
                for output, title in [ self.render(l) for l in lines ]:
                    print(output + "\n")

    def process(self, raw):
        self.write_debug(raw, '1.rnn.txt')
        lines = self.tokenise(raw)
        self.write_debug(lines, '2.tok.txt')
        lines = self.clean(lines)
        self.write_debug(lines, '3.cleaned.txt')
        lines = self.parse(lines)
        self.write_debug(lines, '4.parsed.txt')
        lines = self.length_filter(lines)
        self.write_debug(lines, '5.filtered.txt')
        return lines


    # override this method if the RNN needs a more complicated way
    # to 

    def tokenise(self, sample):
        return sample

    # applies the accept and reject regexps.
    #
    # doesn't filter for length because parse might change it.

    def clean(self, lines):
        accept_re = re.compile(self.cf['accept'])
        reject_re = re.compile(self.cf['reject'], re.IGNORECASE)
        unbalanced_re = re.compile('\([^)]+$')
        cleaned = []
        for raw in lines:
            if not reject_re.search(raw):
                m = accept_re.match(raw)
                if m:
                    cleaned.append(raw)
        return cleaned

    # parse is for model-specific processing

    def parse(self, lines):
        return lines

    # select is used to pick a post from the list of valid results

    def select(self, lines):
        if len(lines) > 5:
            return random.choice(lines[1:-2])
        else:
            return None 

    # render takes an individual line (which could be a string, or a
    # tuple or whatever parse emits) and returns the text of a Mastodon post
    # and an abbreviated version to be injected into a content warning, if 
    # required.
    # it's also called by the logger, so that the logged output is the
    # same as the post. This is all to allow this superclass to drive
    # GLOSSATORY, which pulls the raw output into WORD: definition 

    def render(self, line):
        return line, ''

    # filter the rendered version of the parse results for api length

    def length_filter(self, lines):
        return [ l for l in lines if len(self.render(l)[0]) <= self.max_length ]
  
    def extra_lipo(self, k, chars):
        if chars:
            if random.random() < k:
                c = random.choice(chars)
                return c + self.extra_lipo(k, chars.replace(c, ''))
        return ''

    def lipogram(self):
        forbid = self.cf['suppress']
        if 'suppress_maybe' in self.cf:
            k = 0.2
            if 'suppress_maybe_p' in self.cf:
                k = float(self.cf['suppress_maybe_p'])
            forbid += self.extra_lipo(k, self.cf['suppress_maybe'])
        forbid += forbid.upper()
        self.forbid = forbid
        return forbid

    # Writes a complete log of all output if 'logs' is defined.
    # If 'filter' is defined, runs the output through the filter
    # and append matching lines to 'filterfile' - this is how
    # the entries for the oulipo version are built

    def write_logs(self, t, lines):
        if 'logs' in self.cf:
            timestamp = str(time.time())
            log = self.logfile('log')
            print("Log = {}".format(log))
            with open(log, 'wt') as f:
                f.write("# temperature: {}\n".format(t))
                if self.forbid:
                    f.write("# forbid: {}\n".format(self.forbid))
                for l in lines:
                    r, t = self.render(l)
                    f.write(r + self.log_sep)
        if 'filter' in self.cf:
            fre = re.compile(self.cf['filter'])
            filterf = self.logfile(DEFAULT_FILTER)
            if 'filterfile' in self.cf:
                filterf = self.cf['filterfile']
            print("Filtered = {}".format(filterf))
            with open(filterf, 'a') as f:
                for l in lines:
                    l1, t = self.render(l)
                    if fre.match(l1):
                        f.write(l1 + "\n")

    # dump output from the pipeline to a debug file

    def write_debug(self, debug, ext):
        if self.args.extra:
            debugfile = self.logfile(ext)
            with open(debugfile, 'wt') as f:
                if type(debug) == list:
                    f.writelines('\n--\n'.join(debug))
                else:
                    f.write(debug)


    # the pregen param can be a file or a directory - this tests which
    # it is and returns an array of either the file or the directory's
    # contents

    def get_pregen(self):
        if os.path.isfile(self.args.pregen):
            print(self.args.pregen + " is a file")
            return [ self.args.pregen ]
        if os.path.isdir(self.args.pregen):
            files = []
            with os.scandir(self.args.pregen) as it:
                for entry in it:
                    if entry.is_file() and not entry.name[0] == '.':
                        files.append(os.path.join(self.args.pregen, entry.name))
            files.sort()
            return files
        print(self.args.pregen + " is neither a file nor a directory")
        sys.exit()


    # # Filters the glosses for basic syntax, prohibited terms (this
    # # is for racist language, not the oulipo version, see the write_logs
    # # function for how that works) and unbalanced parentheses

    # def clean_glosses(self, lines):
    #     accept_re = re.compile(self.cf['accept'])
    #     reject_re = re.compile(self.cf['reject'], re.IGNORECASE)
    #     unbalanced_re = re.compile('\([^)]+$')
    #     cleaned = []
    #     for raw in lines:
    #         if not reject_re.search(raw):
    #             m = accept_re.match(raw)
    #             if m:
    #                 word = m.group(1).upper().replace('_', ' ')
    #                 defn = m.group(2)
    #                 if unbalanced_re.search(defn):
    #                     defn += ')'
    #                 if len(word + self.colon + defn) <= self.api.char_limit:
    #                     cleaned.append(( word, defn ))
    #             else:
    #                 print("No match: {}".format(raw))
    #     return cleaned

    def sine_temp(self):
        p = float(self.cf['t_period']) * 60.0 * 60.0
        v = math.sin(time.time() / p)
        return self.cf['t_0'] + v * self.cf['t_amp']

    def rand_temp(self):
        t0 = self.cf['t_0']
        tamp = self.cf['t_amp']
        return t0 - tamp + 2 * random.random() * tamp

    def temperature(self):
        if 't_period' in self.cf:
            return self.sine_temp()
        else:
            return self.rand_temp() 
        

    def spectrum(self):
        sv = self.cf['spectrum'].split()
        self.tstamp = str(time.time())
        low = float(sv[0])
        high = float(sv[1])
        steps = int(sv[2])
        for i in range(steps):
            t = low + (high - low) * (i / (steps - 1))
            output, title = self.generate(t)
            print(output)




    def logfile(self, ext):
        if hasattr(self, 'loop'):
            return os.path.join(self.cf['logs'], "{}.{}.{}".format(self.timestamp, self.loop, ext))
        else:
            return os.path.join(self.cf['logs'], "{}.{}".format(self.timestamp, + ext))


    def run(self):
        self.configure()
        if 'spectrum' in self.cf:
            self.spectrum()
        elif self.args.test:
            t = self.temperature()
            print("Running in test mode, t = {}".format(t))
            self.test(t)
        elif self.args.pregen:
            print("Running in test mode on pre-generated samples")
            self.pregen()
        else:
            output = None
            t = self.temperature()
            output, title = self.generate(t)
            options = {}
            if output:
                if 'content_warning' in self.cf:
                    options['spoiler_text'] = self.cf['content_warning'].format(title)
                self.post(output, options)
            else:
                print("Something went wrong")


        
if __name__ == '__main__':
    rnnb = RnnBot()
    rnnb.run()
