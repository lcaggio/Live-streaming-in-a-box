#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Command-line interface to stream to YouTube
	
	Usage: webserver.py <flags>

    Flag examples:
	  --verbose
	  --bind <interface> | *
	  --port <port>
	  --ffmpeg <binary>
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
import logging,urlparse

# Third party imports
import gflags

# Local imports
import livebox.constants
import livebox.api

################################################################################
# command line flags

FLAGS = gflags.FLAGS
gflags.DEFINE_boolean('verbose',False,"Verbose output")
gflags.DEFINE_string('bind',livebox.constants.NETWORK_BIND,"Network interface or *")
gflags.DEFINE_integer('port',livebox.constants.NETWORK_PORT,"Network port")
gflags.DEFINE_string('wwwroot',os.path.join(root_path,"wwwdocs"),"Web document folder")
gflags.DEFINE_string('ffmpeg',os.path.join(root_path,livebox.constants.STREAMER_EXEC),"ffmpeg binary")
#gflags.DEFINE_string('temproot',None,"Temporary file storage folder")

################################################################################

class Application(livebox.api.APIServer):
	def __init__(self,ffmpeg,bind,port,wwwroot):
		livebox.api.APIServer.__init__(self,ffmpeg,bind,port,wwwroot)

	@property
	def server_url(self):
		return urlparse.urlunparse(("http","%s:%s" % (self.server_name,self.server_port),"/",None,None,None))

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
		if not os.path.isfile(FLAGS.ffmpeg) or not os.access(FLAGS.ffmpeg,os.X_OK):
			raise Error("Invalid --ffmpeg parameter")
		
		
		# Create application
		app = Application(FLAGS.ffmpeg,FLAGS.bind,FLAGS.port,FLAGS.wwwroot)

		# run application
		logging.info("Serving on %s" % app.server_url)
		app.run()

		sys.exit(0)
	except (gflags.FlagsError), e:
		print "Usage error: %s" % e
		sys.exit(-1)

if __name__ == "__main__":
	main(sys.argv)
