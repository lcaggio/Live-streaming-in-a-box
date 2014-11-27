#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Command-line interface to stream to YouTube
	
	Usage: webserver.py <flags>

    Flag examples:
	  --verbose
	  --bind <interface> | *
	  --port <port>
	  --mdns
	  --docroot <folder>
	  --temproot <folder>
	  
	Please see https://github.com/lcaggio/Live-streaming-in-a-box for full
	documentation.

"""

__author__ = "davidthorpe@google.com (David Thorpe)"


# python imports
import os,sys

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

################################################################################
# imports

# Python imports
import logging,tempfile
import time,stat,re,threading

# Third party imports
import gflags

# Local imports
import livebox.constants
import livebox.webserver

################################################################################
# command line flags

FLAGS = gflags.FLAGS
gflags.DEFINE_boolean('verbose',False,"Verbose output")
gflags.DEFINE_string('bind',livebox.constants.NETWORK_BIND,"Network interface or *")
gflags.DEFINE_integer('port',livebox.constants.NETWORK_PORT,"Network port")
gflags.DEFINE_boolean('mdns',True,"Broadcast service availability on network")
gflags.DEFINE_string('wwwroot',os.path.join(root_path,"wwwdocs"),"Web document folder")
gflags.DEFINE_string('temproot',None,"Temporary file storage folder")

################################################################################
# application classes

class Error(Exception):
	pass

class Application(object):
	def __init__(self,bind,port,wwwroot):
		try:
			self._server = livebox.webserver.Server(bind,port,wwwroot)
		except livebox.webserver.Error, e:
			raise Error(e)

	def run(self):
		self._server.run()

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

		# Check input arguments
		if FLAGS.bind=="*":
			FLAGS.bind = ""
		if FLAGS.port < 1:
			raise Error("Invalid --port parameter")
		if not os.path.isdir(FLAGS.wwwroot):
			raise Error("Invalid --wwwroot parameter")
		
		# Create application
		app = Application(FLAGS.bind,FLAGS.port,FLAGS.wwwroot)

		# run application
		app.run()

		sys.exit(0)
	except (Error, gflags.FlagsError), e:
		print "Usage error: %s" % e
		sys.exit(-1)

if __name__ == "__main__":
	main(sys.argv)
