#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python imports
from urlparse import urlparse
import datetime

# Local imports
from . import constants,util

################################################################################

class Control(object):
	""" Livebox control information """

	def __init__(self):
		self._props = { }
		# set default configuration
		self.resolution = constants.CAMERA_RESOLUTION[0][0]
		self.video = constants.STREAMER_VIDEO[0][0]
		self.audio = constants.STREAMER_AUDIO[0][0]
		self.framerate = constants.CAMERA_FRAMERATE
		self.quality = constants.CAMERA_QUALITY
		self.hflip = False
		self.vflip = False

	""" Properties """
	def get_timestamp(self):
		return self._props.get('timestamp')
	timestamp = property(get_timestamp)
	
	def get_url(self):
		return self._props.get('url')
	def set_url(self,value):
		assert value==None or isinstance(value,basestring)
		if not value:
			value = None
		elif urlparse(value).scheme not in constants.STREAMER_URL_SCHEMES:
			raise ValueError("Invalid 'url' value: %s" % value)
		if self._props.get('url') != value:
			self._props['url'] = value
			self._props['timestamp'] = datetime.datetime.now()
	url = property(get_url,set_url)

	def get_resolution(self):
		return self._props.get('resolution')
	def set_resolution(self,value):
		assert isinstance(value,basestring)
		bitrate = util.get_bitrate_for_resolution(value)
		if not bitrate:
			raise ValueError("Invalid 'resolution' value: %s" % value)
		if self._props.get('resolution') != value:
			self._props['resolution'] = value
			self._props['bitrate'] = None
			self._props['timestamp'] = datetime.datetime.now()
	resolution = property(get_resolution,set_resolution)

	def get_bitrate(self):
		if self._props.get('bitrate')==None:
			return util.parse_bitrate(util.get_bitrate_for_resolution(self.resolution))
		else:
			return self._props.get('bitrate')
	def set_bitrate(self,value):
		assert value==None or isinstance(value,(int,long,basestring))
		bitrate = None
		if value:
			bitrate = util.parse_bitrate(value)
			if not bitrate:
				raise ValueError("Invalid 'bitrate' value: %s" % value)
		if bitrate != self._props.get('bitrate'):
			self._props['bitrate'] = bitrate
			self._props['timestamp'] = datetime.datetime.now()
	bitrate = property(get_bitrate,set_bitrate)

	def get_video(self):
		return self._props.get('video')
	def set_video(self,value):
		assert isinstance(value,basestring)
		if value not in [ tuple[0] for tuple in constants.STREAMER_VIDEO ]:
			raise ValueError("Invalid 'video' value: %s" % value)
		if self._props.get('video') != value:
			self._props['video'] = value
			self._props['timestamp'] = datetime.datetime.now()
	video = property(get_video,set_video)

	def get_audio(self):
		return self._props.get('audio')
	def set_audio(self,value):
		assert isinstance(value,basestring)
		if value not in [ tuple[0] for tuple in constants.STREAMER_AUDIO ]:
			raise ValueError("Invalid 'audio' value: %s" % value)
		if self._props.get('audio') != value:
			self._props['audio'] = value
			self._props['timestamp'] = datetime.datetime.now()
	audio = property(get_audio,set_audio)

	def get_framerate(self):
		return self._props.get('framerate')
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
		if self._props.get('framerate') != framerate:
			self._props['framerate'] = framerate
			self._props['timestamp'] = datetime.datetime.now()
	framerate = property(get_framerate,set_framerate)

	def get_quality(self):
		if self._props.get('quality'):
			return self._props.get('quality')
		else:
			return None
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
		if self._props.get('quality') != quality:
			self._props['quality'] = quality
			self._props['timestamp'] = datetime.datetime.now()
	quality = property(get_quality,set_quality)

	def get_hflip(self):
		return self._props.get('hflip')
	def set_hflip(self,value):
		value = util.parse_boolean(value)
		if not isinstance(value,bool):
			raise ValueError("Invalid 'hflip' value")
		if self._props.get('hflip') != value:
			self._props['hflip'] = value
			self._props['timestamp'] = datetime.datetime.now()
	hflip = property(get_hflip,set_hflip)

	def get_vflip(self):
		return self._props.get('vflip')
	def set_vflip(self,value):
		value = util.parse_boolean(value)
		if not isinstance(value,bool):
			raise ValueError("Invalid 'vflip' value")
		if self._props.get('vflip') != value:
			self._props['vflip'] = value
			self._props['timestamp'] = datetime.datetime.now()
	vflip = property(get_vflip,set_vflip)

	""" Methods """
	def as_json(self):
		return {
			'timestamp': self.timestamp.isoformat(),
			'url' : self.url,
			'resolution': self.resolution,
			'bitrate': self.bitrate,
			'video': self.video,
			'audio': self.audio,
			'framerate': self.framerate,
			'quality': self.quality,
			'hflip': self.hflip,
			'vflip': self.vflip
		}
