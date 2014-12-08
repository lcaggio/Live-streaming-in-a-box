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

class Camera(object):
	def __init__(self):
		self._output = None
		self._camera = None

	""" Properties """
	def set_output(self,value):
		assert value==None or isinstance(value,basestring) and value
		if self._output:
			self._output.close()
		if value==None:
			self._output = None
		else:
			self._output = io.open(value,"wb",buffering=65536)
	def get_output(self):
		return self._output
	output = property(get_output,set_output)

	def get_running(self):
		if self._output:
			return True
		else:
			return False
	running = property(get_running)
	
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
	def start(self,filename,control):
		assert isinstance(filename,basestring) and filename
		assert os.path.exists(filename)
		assert isinstance(control,Control)

		""" Get parameters """
		if self.running:
			raise Error("Internal error: Invalid state")

		# Initialize camera
		self._camera_init()

		# Open output file
		self.output = filename

		# Start camera output
		self._camera.resolution = util.get_framesize_for_resolution(control.resolution)
		self._camera.framerate = control.framerate
		self._camera.hflip = control.hflip
		self._camera.vflip = control.vflip
		self._camera.start_recording(
			self.output,
			format=constants.CAMERA_FORMAT,
			profile=constants.CAMERA_PROFILE,
			quality=control.quality,
			bitrate=control.bitrate,
			intra_period=(2*control.framerate),
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
		self.output = None

