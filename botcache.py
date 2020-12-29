#!/usr/bin/env python


import os, os.path, glob, time, random

HISTORY = 'history.txt'
CACHE_PATTERN = '*.log'

class BotCache():

	def __init__(self, options):
		self.dir = options['dir']
		self.cache_max = options['cache_max']
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
		# already used) and those which start with '#'.
		# Returns the valid lines as a list

		cache_files = glob.glob(os.path.join(self.dir, CACHE_PATTERN))
		latest = max(cache_files, key=os.path.getctime)
		with open(latest, 'r') as ch:
			rawcache = [ l.rstrip() for l in ch.readlines() ]
			self.cache = [ l for l in rawcache if not l in self.history and l[0] != '#' ]
			return self.cache


	def get(self):
		"""Returns a cached entry. If there's nothing new in the cache,
		or the cache_max has been exceeded, returns None"""
		self.load_history()
		if not self.history:
			self.history = []
		else:
			if len(self.history) >= self.cache_max:
				self.delete_history()
				return None
		cachelines = self.read_cache()
		if len(cachelines) < 1:
			return None
		else:
			self.write_history(cachelines[0])
			return cachelines[0]

	def put(self, item):
		"""Add a newly generated item to the cache history - this
		assumes that the new cache file containing the item has been
		written to the cache directory by whatever's calling this"""
		self.write_history(item)



def generate_stuff(d):
	"""Generates a file of timestamped random stuff for testing"""
	ts = str(time.time())
	file = os.path.join(d, ts + '.log')
	with open(file, 'w') as fh:
		stuff = []
		for i in range(random.randrange(2, 10)):
			babble = ''.join([ random.choice('AGTC') for k in range(10) ])
			stuff.append(ts + '.' + babble + '.' + str(i))
		fh.writelines("# here are \n# some comments\n")
		fh.writelines([ l + '\n' for l in stuff])
	return stuff[0]




if __name__ == '__main__':
	cache = BotCache({ 'dir': './cache_test', 'cache_max': 8})

	from_cache = cache.get()
	if from_cache:
		print("cache> {}".format(from_cache))
	else:
		fresh = generate_stuff('./cache_test')
		print("fresh> {}".format(fresh))
		cache.put(fresh)





