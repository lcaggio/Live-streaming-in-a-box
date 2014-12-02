#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python imports
import os,re,tempfile,datetime

# Local imports
from . import constants

################################################################################

# Optional psutil import
IMPORT_PSUTIL = True
try:
    import psutil
except ImportError, e:
	IMPORT_PSUTIL = False

################################################################################

def system_info():
	""" Return system information """
	if IMPORT_PSUTIL:
		cpu = psutil.Process(os.getpid()).get_cpu_percent()
	else:
		cpu = None

	return {
		"cpu": cpu
	}

################################################################################

class FIFO(object):
	""" Create and maintain a FIFO file """
	def __init__(self,filename=constants.FIFO_NAME):
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

################################################################################

def parse_duration_timedelta(value):
	""" Return timedelta from duration value """
	if isinstance(value,(int,long)) and value >= 0:
		return datetime.timedelta(secs=value)
	if isinstance(value,datetime.timedelta) and value >= 0:
		return value
	if not isinstance(value,basestring):
		raise Error("Invalid time duration value")
	# TODO

def parse_bitrate(value):
	""" Returns bitrate in bytes """
	if isinstance(value,(int,long)) and value > 0:
		return long(value)
	elif isinstance(value,basestring) and value:
		m = re.match(r"^\s*(\d+)\s*$",value)
		if m:
			v = long(m.group(1))
			if v > 0: return v
		m = re.match(r"^\s*(\d+)\s*(k|kb|kbps)\s*$",value)
		if m:
			v = long(m.group(1)) * 1000
			if v > 0: return v
		m = re.match(r"^\s*(\d+)\s*(M|Mb|Mbps)\s*$",value)
		if m:
			v = long(m.group(1)) * 1000 * 1000
			if v > 0: return v
	return None

def parse_boolean(value):
	""" Returns a boolean value """
	if isinstance(value,(bool,int,long)):
		return bool(value)
	if isinstance(value,basestring):
		if not value:
			return False
		m = re.match(r"^\s*(0|f|F|false|False|FALSE|n|N|No|NO)\s*$",value)
		if m:
			return False
		m = re.match(r"^\s*(1|t|T|true|True|TRUE|y|Y|Yes|YES)\s*$",value)
		if m:
			return True
	return None

def get_bitrate_for_resolution(value):
	for tuple in constants.CAMERA_RESOLUTION:
		if tuple[0]==value:
			return tuple[3]
	return None

def get_framesize_for_resolution(value):
	for tuple in constants.CAMERA_RESOLUTION:
		if tuple[0]==value:
			return (tuple[1],tuple[2])
	return None


