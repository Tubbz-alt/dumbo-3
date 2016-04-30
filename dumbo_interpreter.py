#!/usr/bin/env python2
import sys

def execute(filename, output):
	if output != None:
		output.write("TODO\n")


if len(sys.argv) != 4:
	print >>sys.stdout, "usage:", sys.argv[0], "data template output"
	sys.exit(1)
else:
	try:
		f = file(sys.argv[3], "w")
		try:
			execute(sys.argv[1], None)
			execute(sys.argv[2], f)
		finally:
			f.close()
	except (IOError, OSError) as e:
		print >>sys.stdout, e
		sys.exit(e.errno)
