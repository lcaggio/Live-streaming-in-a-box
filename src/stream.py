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
"""

__author__ = "davidthorpe@google.com (David Thorpe)"

# python imports
import os,sys,logging,tempfile

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
import time,stat,re,threading

# Third party imports
import gflags

# Local imports
import livebox.constants
import livebox.camera
import livebox.streamer

################################################################################
# command line flags

FLAGS = gflags.FLAGS
gflags.DEFINE_boolean('verbose',False,"Verbose output")
gflags.DEFINE_string('resolution',livebox.constants.CAMERA_RESOLUTION[0][0],"Camera resolution")
gflags.DEFINE_integer('fps',livebox.constants.CAMERA_FRAMERATE,"Frames per second")
gflags.DEFINE_string('bitrate',None,"Video bitrate")
gflags.DEFINE_string('audio',livebox.constants.STREAMER_AUDIO[0][0],"Audio channel content")
gflags.DEFINE_integer('quality',livebox.constants.CAMERA_QUALITY,"Camera quality parameter")

################################################################################
# application classes

class Error(Exception):
	pass

class FIFO(object):
	""" Create and maintain a FIFO file """
	def __init__(self,filename=livebox.constants.FIFO_NAME):
		self._temp_path = tempfile.mkdtemp()
		self._fifo_path = os.path.join(self._temp_path,filename)
		try:
			os.mkfifo(self._fifo_path)
		except OSError, e:
			raise Error(e)

	@property
	def filename(self):
		return self._fifo_path

	def close(self):
		try:
			os.remove(self._fifo_path)
			os.rmdir(self._temp_path)
		except OSError, e:
			raise Error(e)

class Application(object):
	def __init__(self,argv,package_path=None,resolution=None,framerate=None,bitrate=None,audio=None,quality=None):
		assert isinstance(argv,list)
		assert isinstance(resolution,tuple)
		assert isinstance(audio,tuple)
		assert bitrate==None or isinstance(bitrate,(int,long,basestring))
		assert isinstance(package_path,basestring) and os.path.isdir(package_path)
		assert len(argv)==2

		# set parameters
		self.framerate = framerate
		self.resolution = resolution
		self.audio = audio
		self.quality = quality
		if bitrate:
			self.bitrate = bitrate
		self.url = argv[1]
		
		# set camera and streamer objects
		self.camera = livebox.camera.Camera()
		self.streamer = livebox.streamer.Streamer(ffmpeg=os.path.join(package_path,livebox.constants.STREAMER_EXEC),audio_flags=self.audio[1:])

	""" Private methods """
	@classmethod
	def _touch_file(self,filename):
		assert isinstance(filename,basestring)
		try:
			with open(filename,'a'):
				now = time.time()
				os.utime(filename,(now,now))
		except IOError, e:
			raise Error(e)

	@classmethod
	def parse_bitrate(self,bitrate):
		assert isinstance(bitrate,(int,long,basestring))
		if isinstance(bitrate,(int,long)) and bitrate > 0:
			return long(bitrate)
		m = re.match(r"^\s*(\d+)\s*$",bitrate)
		if m:
			v = long(m.group(1))
			if v > 0: return v
		m = re.match(r"^\s*(\d+)\s*(k|kb|kbps)\s*$",bitrate)
		if m:
			v = long(m.group(1)) * 1000
			if v > 0: return v
		m = re.match(r"^\s*(\d+)\s*(M|Mb|Mbps)\s*$",bitrate)
		if m:
			v = long(m.group(1)) * 1000 * 1000
			if v > 0: return v
		return None

	""" Properties """
	def get_filename(self):
		return self._filename
	def set_filename(self,value):
		assert isinstance(value,basestring) and value
		self._filename = value
	filename = property(get_filename,set_filename)

	def get_resolution(self):
		return self._resolution
	def set_resolution(self,value):
		assert isinstance(value,tuple)
		self._resolution = value
		self.bitrate = value[3]
	resolution = property(get_resolution,set_resolution)

	def get_audio(self):
		return self._audio
	def set_audio(self,value):
		assert isinstance(value,tuple)
		self._audio = value
	audio = property(get_audio,set_audio)

	def get_framesize(self):
		assert isinstance(self.resolution,tuple)
		return (self.resolution[1],self.resolution[2])
	framesize = property(get_framesize)

	def set_framerate(self,value):
		assert isinstance(value,int) and value > 0
		self._framerate = value
	def get_framerate(self):
		return self._framerate
	framerate = property(get_framerate,set_framerate)

	def set_quality(self,value):
		assert value==None or (isinstance(value,int) and value > 0)
		self._quality = value
	def get_quality(self):
		return self._quality
	quality = property(get_quality,set_quality)

	def set_bitrate(self,value):
		assert isinstance(value,(int,long,basestring))
		self._bitrate = self.parse_bitrate(value)
	def get_bitrate(self):
		return self._bitrate
	bitrate = property(get_bitrate,set_bitrate)

	""" Public methods """
	@classmethod
	def resolution_tuple(self,key):
		for tuple in livebox.constants.CAMERA_RESOLUTION:
			if tuple[0]==key: return tuple
		return None
	@classmethod
	def resolution_values(self):
		return [tuple[0] for tuple in livebox.constants.CAMERA_RESOLUTION]
	@classmethod
	def audio_tuple(self,key):
		for tuple in livebox.constants.STREAMER_AUDIO:
			if tuple[0]==key: return tuple
		return None
	@classmethod
	def audio_values(self):
		return [tuple[0] for tuple in livebox.constants.STREAMER_AUDIO]

	def run(self):
		logging.info("RUNNING resolution=%s fps=%s bitrate=%s quality=%s audio=%s" % (self.resolution,self.framerate,self.bitrate,self.quality,self.audio))
		
		# create a FIFO object
		output = FIFO()
		camera_thread = threading.Thread(target=self.camera.capture,args=(output.filename,self.framesize,self.framerate,self.bitrate,self.quality))
		streamer_thread = threading.Thread(target=self.streamer.stream,args=(output.filename,self.framerate,self.bitrate,self.url))

		camera_thread.daemon = True
		streamer_thread.daemon = True
		
		camera_thread.start()
		streamer_thread.start()
		
		# wait until both threads are up and running
		logging.info("STARTING Application.run filename=%s" % output.filename)
		while not self.camera.running and not self.streamer.running:
			time.sleep(1)
		
		# wait until camera thread has completed
		while self.camera.running:
			time.sleep(1)

		# TODO: stop streamer thread
		fifo.close()

		logging.info("STOPPED Application.run")


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
		if not FLAGS.fps > 0:
			raise Error("Invalid or missing argument: --fps")		
		resolution_tuple = Application.resolution_tuple(FLAGS.resolution)
		if not resolution_tuple:
			raise Error("Invalid or missing: --resolution (valid values are %s)" % ",".join(Application.resolution_values()))
		audio_tuple = Application.audio_tuple(FLAGS.audio)
		if not audio_tuple:
			raise Error("Invalid or missing: --audio (valid values are %s)" % ",".join(Application.audio_values()))
		if FLAGS.bitrate and not Application.parse_bitrate(FLAGS.bitrate):
			raise Error("Invalid argument: --bitrate")
		
		# Create application
		application = Application(argv,package_path=root_path,resolution=resolution_tuple,framerate=FLAGS.fps,bitrate=FLAGS.bitrate,audio=audio_tuple,quality=FLAGS.quality)
		application.run()
		sys.exit(0)
	except (Error, gflags.FlagsError), e:
		print "Usage error: %s" % e
		sys.exit(-1)

if __name__ == "__main__":
	main(sys.argv)
