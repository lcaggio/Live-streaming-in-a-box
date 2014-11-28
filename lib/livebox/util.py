#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python imports
import os,re
import datetime

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

def parse_duration_timedelta(value):
	""" Return timedelta from duration value """
	if isinstance(value,(int,long)) and value >= 0:
		return datetime.timedelta(secs=value)
	if isinstance(value,datetime.timedelta) and value >= 0:
		return value
	if not isinstance(value,basestring):
		raise Error("Invalid time duration value")
	# TODO

