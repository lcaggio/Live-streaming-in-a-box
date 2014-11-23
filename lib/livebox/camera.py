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

# Third party imports
import picamera

# Local imports
from . import constants

################################################################################
# Camera class

class Camera(object):
	def __init__(self):
		self.running = False

	def capture(self,filename=None,framesize=None,framerate=constants.CAMERA_FRAMERATE,bitrate=None,quality=constants.CAMERA_QUALITY,profile=constants.CAMERA_PROFILE[0]):
		assert isinstance(filename,basestring) and filename
		assert isinstance(framesize,tuple) and len(framesize)==2
		assert isinstance(framerate,int) and framerate > 0
		assert quality==None or (isinstance(quality,int) and quality > 0)
		assert isinstance(profile,basestring) and profile in constants.CAMERA_PROFILE
		assert bitrate==None or (isinstance(bitrate,(int,long)) and bitrate > 0)

		self.running = True
		with io.open(filename,"wb",buffering=65536) as output:
			with picamera.PiCamera() as camera:
				camera.resolution = framesize
				camera.framerate = framerate
				camera.start_recording(output,format=constants.CAMERA_FORMAT,quality=quality,profile=profile,intra_period=(2*framerate),inline_headers=True,bitrate=bitrate)
				logging.debug("Started capture")
				camera.wait_recording(timeout=3600 * 10)
				logging.debug("Finished capture, stopping recording")
				camera.stop_recording()
		self.running = False

