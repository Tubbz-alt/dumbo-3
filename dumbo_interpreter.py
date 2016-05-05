#!/usr/bin/env python2
import sys
from parser import yacc, Context, FakeOutput

def execute(filename, context):
	with open(filename, "r") as file:
		source = file.read()
	yacc.parse(source)(c)


if len(sys.argv) != 4:
	print >>sys.stdout, "usage:", sys.argv[0], "data template output"
	sys.exit(1)
else:
	try:
		f = file(sys.argv[3], "w")
		try:
			c = Context(FakeOutput())
			execute(sys.argv[1], c)
			c.out = f
			execute(sys.argv[2], c)
		finally:
			f.close()
	except (IOError, OSError) as e:
		print >>sys.stdout, e
		sys.exit(e.errno)
