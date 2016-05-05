#!/usr/bin/env python2
import sys
from parser import yacc, Context

class TestOutput(object):
	def __init__(self, name, expected):
		self.out = ""
		self._name = name
		self._exp = expected
	def write(self, s):
		assert(isinstance(s, str))
		self.out += s
	def test(self):
		r = self.out == self._exp
		tr = "passed" if r else "***FAILED***"
		print self._name, tr
		if not r:
			print "\texpected:", repr(self._exp)
			print "\tgot:", repr(self.out)
			print
		return r

if __name__ == "__main__":
	import sys
	import os
	if len(sys.argv) > 1:
		res = True
		for f in sys.argv[1:]:
			base = os.path.splitext(f)[0]
			exp = base + ".exp"
			if os.path.exists(exp) and exp!=f:
				with open(exp, "r") as file:
					expected = file.read()
				with open(f, "r") as file:
					source = file.read()
				o = TestOutput(os.path.basename(base), expected)
				c = Context(o)
				yacc.parse(source)(c)
				res = res and o.test()
		sys.exit(int(not res))
	else:
		print >>sys.stderr, "usage: %s test [test...]" % sys.argv[0]
		sys.exit(2)
