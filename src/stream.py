#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Command-line interface to stream to YouTube
	
	Usage: stream.py <flags>
"""

__author__ = "davidthorpe@google.com (David Thorpe)"

# python imports
import os,sys,logging

# add python libraries:
# 'lib' for shared modules
# 'third_party' for external (third party) modules
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
code_paths = [
	os.path.join(root_path,'lib'),
	os.path.join(root_path,'third_party')
]
for path in code_paths:
	if (path not in sys.path) and os.path.exists(path): sys.path.insert(0,path)

# Python imports
import time

# Third party imports
import gflags

# Local imports
import livebox.constants
import livebox.camera

# command line flags
FLAGS = gflags.FLAGS
gflags.DEFINE_boolean('verbose',False,"Verbose output")
gflags.DEFINE_string('stream',None,"YouTube Stream Name")

class Application(object):
	def __init__(self,argv):
		assert isinstance(argv,list)
		pass
	def run(self):
		logging.info("RUNNING")
		pass

################################################################################
# main method

def main(argv):
	try:
		argv = FLAGS(argv)
		
		# set logging verbosity level
		if FLAGS.verbose:
			logging.basicConfig(level=logging.DEBUG)
		else:
			logging.basicConfig(level=logging.INFO)

		# Create application and run it
		application = Application(argv)
		application.run()
		
		sys.exit(0)
	except gflags.FlagsError, e:
		print "Usage error: %s" % e
		sys.exit(-1)

if __name__ == "__main__":
	main(sys.argv)
