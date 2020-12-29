#!/usr/bin/env python


import os, os.path, glob, time, random

HISTORY = 'history.txt'
CACHE_PATTERN = '*.log'

class BotCache():

	def __init__(self, options):
		self.dir = options['dir']
		self.histfile = os.path.join(self.dir, HISTORY)
		self.history = None

	def load_history(self):
		try:
			with open(self.histfile, 'r') as cfh:
				self.history = [ l.rstrip() for l in cfh.readlines() ]
				return self.history
		except OSError as e:
			return None

	def write_history(self, item):
		if not self.history:
			self.history = [ item ]
		else:
			self.history.append(item)
		with open(self.histfile, 'w') as cfh:
			cfh.writelines([ l + '\n' for l in self.history])
		
	def delete_history(self):
		ts = str(time.time())
		self.history = None
		try:
			os.rename(self.histfile, self.histfile + '.' + ts)
		except OSError as e:
			print("rename cache history error: " + str(e))

	def read_cache(self):
	
		# find the most recent file in the cache dir which matches
		# CACHE_PATTERN, read all the lines, and filter out those
		# which are in the current cache history (ie they've been
		# already used).  Returns the valid lines as a list

		cache_files = glob.glob(os.path.join(self.dir, CACHE_PATTERN))
		latest = max(cache_files, key=os.path.getctime)
		with open(latest, 'r') as ch:
			rawcache = [ l.rstrip() for l in ch.readlines() ]
			self.cache = [ l for l in rawcache if not l in self.history ]
			return self.cache


def generate_stuff(d):
	print("Generating more stuff")
	ts = str(time.time())
	file = os.path.join(d, ts + '.log')
	with open(file, 'w') as fh:
		stuff = []
		for i in range(random.randrange(2, 10)):
			babble = ''.join([ random.choice('AGTC') for k in range(10) ])
			stuff.append(ts + '.' + babble + '.' + str(i))
		fh.writelines([ l + '\n' for l in stuff])
	return stuff[0]




if __name__ == '__main__':
	cache = BotCache({ 'dir': './cache_test'})
	max_cache = 8
	history = cache.load_history()
	if not history or len(history) == max_cache:
		print("History not found or exceeded {} items".format(max_cache))
		cache.delete_history()
		fresh = generate_stuff('./cache_test')
		print("fresh> {}".format(fresh))
		cache.write_history(fresh)
	else:
		cachelines = cache.read_cache()
		if len(cachelines) < 1:
			fresh = generate_stuff('./cache_test')
			print("fresh> {}".format(fresh))
			cache.write_history(fresh)
		else:
			print("cache> {}".format(cachelines[0]))
			cache.write_history(cachelines[0])





