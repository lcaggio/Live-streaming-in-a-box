#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Live Streaming in a Box
    -----------------------
	Constants for livebox
"""
__author__ = "davidthorpe@google.com (David Thorpe)"

# Python imports
import io,logging

# Optional picamera import
IMPORT_PICAMERA = True
try:
    import picamera
except ImportError, e:
	IMPORT_PICAMERA = False

# Local imports
from . import constants

################################################################################

class Error(Exception):
	pass

################################################################################

class Camera(object):
	def __init__(self):
		self.running = False
		self._output = None
		self._camera = None

	""" Properties """
	def set_running(self,value):
		assert isinstance(value,bool)
		self._running = value
	def get_running(self):
		return self._running
	running = property(get_running,set_running)
	
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
	def start(self,filename=None,framesize=None,framerate=constants.CAMERA_FRAMERATE,bitrate=None,quality=constants.CAMERA_QUALITY,profile=constants.CAMERA_PROFILE[0]):
		assert isinstance(filename,basestring) and filename
		assert isinstance(framesize,tuple) and len(framesize)==2
		assert isinstance(framerate,int) and framerate > 0
		assert quality==None or (isinstance(quality,int) and quality > 0)
		assert isinstance(profile,basestring) and profile in constants.CAMERA_PROFILE
		assert bitrate==None or (isinstance(bitrate,(int,long)) and bitrate > 0)

		if self._output:
			raise Error("Internal error: Invalid state")
		self._camera_init()
		self._output = io.open(filename,"wb",buffering=65536)
		self._camera.resolution = framesize
		self._camera.framerate = framerate
		self._camera.start_recording(self._output,format=constants.CAMERA_FORMAT,quality=quality,profile=profile,intra_period=(2*framerate),inline_headers=True,bitrate=bitrate)
		self.running = True

#				camera.wait_recording(timeout=3600 * 10)

	def stop(self):
		if not IMPORT_PICAMERA:
			raise Error("Camera not supported")
		self._camera_init()
		try:
			self._camera.stop_recording()
		except picamera.exc.PiCameraNotRecording:
			raise Error("Internal error: Invalid state")
		self._output.close()
		self._output = None
		self.running = False

