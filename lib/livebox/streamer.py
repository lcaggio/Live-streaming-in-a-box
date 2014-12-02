#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Live Streaming in a Box
    -----------------------
	Streamer - takes an input and streams/converts using FFMPEG
"""
__author__ = "davidthorpe@google.com (David Thorpe)"

# Python imports
import os,logging, subprocess, threading, Queue, time, re

# Local imports
from . import util,constants,Control

################################################################################

class Error(Exception):
	pass

################################################################################

class Streamer(object):
	def __init__(self,ffmpeg=None):
		assert isinstance(ffmpeg,basestring) and ffmpeg
		assert os.path.exists(ffmpeg) and os.path.isfile(ffmpeg)
		self._ffmpeg = ffmpeg
		self._input = None
		self._queue = Queue.Queue()
	
	""" Properties """
	def set_input(self,value):
		assert value==None or isinstance(value,basestring) and value
		if value==None:
			self._input = None
		else:
			self._input = value
	def get_input(self):
		return self._input
	input = property(get_input,set_input)

	def get_running(self):
		if self._input:
			return True
		else:
			return False
	running = property(get_running)
	
	
	""" Private methods """
	def _ffmpeg_output(self,process):
		logging.debug("_ffmpeg_output started")
		line = process.stderr.readline()
		while line:
			m = re.match(r"\s*frame=\s*(\S+)\s+fps=\s*(\S+)\s+q=(\S+)\s+size=\s*(\S+)\s+time=\s*(\S*)\s+bitrate=\s*(\S*)",line)
			if m:
				self._queue.put_nowait({
					"frame": long(m.group(1)),
					"fps": float(m.group(2)),
					"q": float(m.group(3)),
					"size": m.group(4),
					"time": m.group(5),
					"bitrate": m.group(6)
				})
			line = process.stderr.readline()
		logging.debug("_ffmpeg_output terminating")

	def _flags_input_audio(self,control):
		assert isinstance(control,Control)
		return util.get_flags_for_audio(control.audio)

	def _flags_input_video(self,control):
		assert isinstance(control,Control)
		return [ "-re","-f %s" % constants.CAMERA_FORMAT,"-r %s" % control.framerate,"-i \"%s\"" % self._input ]

	def _flags_output(self,control):
		assert isinstance(control,Control)
		return [
			"-c:v copy","-b:v %s" % control.bitrate,"-c:a aac","-b:a %s" % constants.STREAMER_AUDIO_BITRATE,
			"-map 0:0","-map 1:0","-strict experimental",
			"-f flv"
		]

	def start(self,filename,control):
		assert isinstance(filename,basestring) and filename
		assert os.path.exists(filename)
		assert isinstance(control,Control)

		""" Get parameters """
		if self.running:
			raise Error("Internal error: Invalid state")
	
		# Open input file
		self.input = filename
	
		flags = [ ]
		flags.extend(self._flags_input_video(control))
		flags.extend(self._flags_input_audio(control))
		flags.extend(self._flags_output(control))
		
		logging.debug("start: flags: %s" % flags)
	
	def stop(self):
		self.input = None

	def stream(self,filename=None,framerate=None,bitrate=None,url=None):
		assert isinstance(filename,basestring) and filename
		assert os.path.exists(filename)
		assert isinstance(framerate,(int,long)) and framerate > 0
		assert isinstance(bitrate,(int,long)) and bitrate > 0
		assert isinstance(url,basestring) and url
		flags.extend()
		flags.append(url)
		# open the subprocess
		ffmpeg = [ self._ffmpeg ]
		ffmpeg.extend(flags)
		
		# run the process, and in the background, read the status from stderr
		logging.debug("Streamer.stream: execute: %s" % " ".join(ffmpeg))
		proc = subprocess.Popen(" ".join(ffmpeg),shell=True,universal_newlines=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		stderr_thread = threading.Thread(target=self._ffmpeg_output,args=(proc,))
		stderr_thread.daemon = True
		stderr_thread.start()
		
		# wait for subprocess to complete
		logging.debug("STARTING FFMPEG")
		while not proc.poll():
			try:
				item = self._queue.get(True,1.0)
				logging.debug("Status: %s" % item)
			except Queue.Empty:
				pass

		returncode = proc.poll()
		logging.debug("COMPLETED FFMPEG, return code %s" % returncode)
		return returncode


	
#  -f h264  -r ${FPS} -i "${FIFO_FILE}" \
#  -re \
#  -f lavfi -i "sine=frequency=1000:duration=0" \
#  -c:v copy -b:v ${KBPS}k -c:a aac -b:a 64k \
#  -map 0:0 -map 1:0  -strict experimental \
#  -f flv "${STREAM_URL}"
