#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Command-line interface to stream to YouTube
	
	Usage: stream.py <flags> <url>

    Flag examples:
	  --verbose
	  --output <filename>
	  --resolution 240p | 360p | 480p | 720p | 1080p
	  --audio silence | 1kHz
	  --fps 15 | 25 | 30
	  --quality 10-40
	  --bitrate 800kpbs 1M etc.
	  --vflip
	  --hflip
	  
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
import logging,pprint,signal,time

# Third party imports
import gflags

# Local imports
import livebox,livebox.streamer,livebox.util

################################################################################
# command line flags

FLAGS = gflags.FLAGS
gflags.DEFINE_boolean('verbose',False,"Verbose output")
gflags.DEFINE_string('resolution',livebox.constants.CAMERA_RESOLUTION[0][0],"Camera resolution")
gflags.DEFINE_integer('framerate',livebox.constants.CAMERA_FRAMERATE,"Frames per second")
gflags.DEFINE_string('bitrate',None,"Video bitrate")
gflags.DEFINE_string('audio',livebox.constants.STREAMER_AUDIO[0][0],"Audio channel content")
gflags.DEFINE_string('video',livebox.constants.STREAMER_VIDEO[0][0],"Video channel content")
gflags.DEFINE_integer('quality',livebox.constants.CAMERA_QUALITY,"Camera quality parameter")
gflags.DEFINE_boolean('hflip',False,"Horizonal image flip")
gflags.DEFINE_boolean('vflip',False,"Vertical image flip")
gflags.DEFINE_string('ffmpeg',os.path.join(root_path,livebox.constants.STREAMER_EXEC),"ffmpeg binary")

################################################################################
# application classes

class Application(object):
	def __init__(self,control,ffmpeg=None):
		assert isinstance(control,livebox.Control)

		# set streamer objects
		self.control = control
		self.streamer = livebox.streamer.Streamer(ffmpeg)

		# set signal handlers
		signal.signal(signal.SIGINT,self.signal_handler)
		signal.signal(signal.SIGTERM,self.signal_handler)

	""" Methods """
	def signal_handler(self,num,stack):
		logging.debug("Caught signal %d" % num)
		self.streamer.stop()

	def run(self):
		fifo = livebox.util.FIFO()
		filename = fifo.filename
		logging.info("RUNNING resolution=%s fps=%s bitrate=%s quality=%s audio=%s" % (self.control.resolution,self.control.framerate,self.control.bitrate,self.control.quality,self.control.audio))
		self.streamer.start(filename,self.control)
		while self.streamer.running:
			time.sleep(0.5)
		fifo.close()

		returnvalue = self.streamer.returnvalue

		logging.info("STOPPED, returncode = %s" % str(returnvalue))
		return self.streamer.returnvalue

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

		# check some parameters
		if len(argv) != 2:
			raise gflags.FlagsError("Missing URL")

		# Set control parameters
		control = livebox.Control()
		try:
			control.url = argv[1]
			for key in ('resolution','framerate','bitrate','audio','quality','hflip','vflip'):
				value = getattr(FLAGS,key)
				setattr(control,key,value)
		except ValueError, e:
			raise gflags.FlagsError(e)

		logging.debug(pprint.pformat(control.as_json()))

		# Run application
		application = Application(control,ffmpeg=FLAGS.ffmpeg)

		# Deal with the return value
		(returncode,status) = application.run()
		if returncode:
			logging.error(status)
		sys.exit(returncode)
	except gflags.FlagsError, e:
		print "Usage error: %s" % e
		sys.exit(-1)

if __name__ == "__main__":
	main(sys.argv)
