#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python imports
from urlparse import urlparse
import pprint

# Local imports
from . import constants,util

################################################################################

class Control(object):
	""" Livebox control information """

	def __init__(self):
		# set default configuration
		self.url = None
		self.resolution = constants.CAMERA_RESOLUTION[0][0]
		self.video = constants.STREAMER_VIDEO[0][0]
		self.audio = constants.STREAMER_AUDIO[0][0]
		self.framerate = constants.CAMERA_FRAMERATE
		self.quality = constants.CAMERA_QUALITY

	""" Properties """
	def get_url(self):
		return self._url
	def set_url(self,value):
		assert value==None or isinstance(value,basestring)
		if not value:
			value = None
		elif urlparse(value).scheme not in constants.STREAMER_URL_SCHEMES:
			raise ValueError("Invalid 'url' value: %s" % value)
		self._url = value
	url = property(get_url,set_url)

	def get_resolution(self):
		return self._resolution
	def set_resolution(self,value):
		assert isinstance(value,basestring)
		bitrate = util.get_bitrate_for_resolution(value)
		if not bitrate:
			raise ValueError("Invalid 'resolution' value: %s" % value)
		self._resolution = value
		self._bitrate = None
	resolution = property(get_resolution,set_resolution)

	def get_bitrate(self):
		if self._bitrate==None:
			return util.parse_bitrate(util.get_bitrate_for_resolution(self.resolution))
		else:
			return self._bitrate
	def set_bitrate(self,value):
		assert value==None or isinstance(value,(int,long,basestring))
		bitrate = None
		if value:
			bitrate = util.parse_bitrate(value)
			if not bitrate:
				raise ValueError("Invalid 'bitrate' value: %s" % value)
		self._bitrate = bitrate
	bitrate = property(get_bitrate,set_bitrate)

	def get_video(self):
		return self._video
	def set_video(self,value):
		assert isinstance(value,basestring)
		if value not in [ tuple[0] for tuple in constants.STREAMER_VIDEO ]:
			raise ValueError("Invalid 'video' value: %s" % value)
		self._video = value
	video = property(get_video,set_video)

	def get_audio(self):
		return self._audio
	def set_audio(self,value):
		assert isinstance(value,basestring)
		if value not in [ tuple[0] for tuple in constants.STREAMER_AUDIO ]:
			raise ValueError("Invalid 'audio' value: %s" % value)
		self._audio = value
	audio = property(get_audio,set_audio)

	def get_framerate(self):
		return self._framerate
	def set_framerate(self,value):
		assert value==None or isinstance(value,(int,long,basestring))
		framerate = None
		if value==None:
			framerate = int(constants.CAMERA_FRAMERATE)
		if isinstance(value,(int,long)) and value > 0:
			framerate = value
		elif isinstance(value,basestring):
			try:
				framerate = int(value)
			except TypeError:
				pass
		if not framerate:
			raise ValueError("Invalid 'framerate' value: %s" % value)
		self._framerate = framerate
	framerate = property(get_framerate,set_framerate)

	def get_quality(self):
		return self._quality
	def set_quality(self,value):
		assert value==None or isinstance(value,(int,long,basestring))
		quality = None
		if value==None:
			quality = 0
		if isinstance(value,(int,long)) and value > 0:
			quality = value
		elif isinstance(value,basestring):
			try:
				quality = int(value)
			except TypeError:
				pass
		if quality==None:
			raise ValueError("Invalid 'quality' value: %s" % value)
		self._quality = quality
	quality = property(get_quality,set_quality)

	""" Methods """
	def as_json(self):
		return {
			'url' : self.url,
			'resolution': self.resolution,
			'bitrate': self.bitrate,
			'video': self.video,
			'audio': self.audio,
			'framerate': self.framerate,
			'quality': self.quality
		}

	def __str__(self):
		return pprint.pformat(self._config)


