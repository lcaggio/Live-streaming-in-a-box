#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Live Streaming in a Box
"""
__author__ = "davidthorpe@google.com (David Thorpe)"

# Python imports
import io,os,logging

# Optional picamera import
IMPORT_PICAMERA = True
try:
    import picamera
except ImportError, e:
	IMPORT_PICAMERA = False

# Local imports
from . import Control,constants,util

################################################################################

class Error(Exception):
	pass

################################################################################

class Base(object):

	""" Constructor """
	def __init__(self,filename,control):
		assert isinstance(filename,basestring) and filename
		assert os.path.exists(filename)
		assert isinstance(control,Control)
		self._control = control
		self._filehandle = None
		self.filename = filename

	""" Properties """
	def set_filename(self,value):
		assert value==None or isinstance(value,basestring) and value
		if self._filehandle:
			self._filehandle.close()
		if value==None:
			self._filename = None
			self._filehandle = None
		else:
			self._filehandle = io.open(value,"wb",buffering=65536)
			self._filename = value
	def get_filename(self):
		return self._filename
	filename = property(get_filename,set_filename)

	def get_filehandle(self):
		return self._filehandle
	filehandle = property(get_filehandle)

	def get_running(self):
		if self._filehandle:
			return True
		else:
			return False
	running = property(get_running)

	def get_control(self):
		return self._control
	control = property(get_control)

	def get_streamer_flags(self):
		return [ ]
	streamer_flags = property(get_streamer_flags)

	""" Methods """
	def start(self):
		logging.error("start: Not implemented")

	def stop(self):
		logging.error("stop: Not implemented")

################################################################################

class File(Base):

	""" Properties """
	def get_streamer_flags(self):
		return [ "-re","-f %s" % constants.CAMERA_FORMAT,"-r %s" % self.control.framerate,"-i \"%s\"" % self.filename ]
	streamer_flags = property(get_streamer_flags)


################################################################################

class Camera(Base):
	def __init__(self,*args):
		Base.__init__(self,*args)
		self._camera = None

	""" Properties """
	def get_streamer_flags(self):
		return [ "-re","-f %s" % constants.CAMERA_FORMAT,"-r %s" % self.control.framerate,"-i \"%s\"" % self.filename ]
	streamer_flags = property(get_streamer_flags)
	
	""" Private methods """
	def _camera_init(self):
		if self._camera:
			return
		if not IMPORT_PICAMERA:
			raise Error("Camera not supported")
		try:
			self._camera = picamera.PiCamera()
		except picamera.exc.PiCameraError, e:
			raise Error("%s" % e)

	""" Methods """
	def start(self):
		""" Get parameters """
		if self.running:
			raise Error("Internal error: Invalid state")

		# Initialize camera
		self._camera_init()

		# Start camera output
		self._camera.resolution = util.get_framesize_for_resolution(self.control.resolution)
		self._camera.framerate = self.control.framerate
		self._camera.hflip = self.control.hflip
		self._camera.vflip = self.control.vflip
		self._camera.start_recording(
			self.filehandle,
			format=constants.CAMERA_FORMAT,
			profile=constants.CAMERA_PROFILE,
			quality=self.control.quality,
			bitrate=self.control.bitrate,
			intra_period=(2 * self.control.framerate),
			inline_headers=True
		)
#		camera.wait_recording(timeout=3600 * 10)

	def stop(self):
		if not IMPORT_PICAMERA:
			raise Error("Camera not supported")
		self._camera_init()
		try:
			self._camera.stop_recording()
		except picamera.exc.PiCameraNotRecording:
			raise Error("Internal error: Invalid state")
		self.filename = None


