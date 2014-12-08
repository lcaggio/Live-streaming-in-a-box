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
import livebox.input

################################################################################

class Error(Exception):
	pass

################################################################################

class Streamer(object):
	def __init__(self,ffmpeg=None):
		assert isinstance(ffmpeg,basestring) and ffmpeg
		assert os.path.exists(ffmpeg) and os.path.isfile(ffmpeg)
		self._ffmpeg = ffmpeg
		self._queue = Queue.Queue()
		self.input = None
		self.returnvalue = None
	
	""" Properties """
	def set_input(self,value):
		assert value==None or isinstance(value,livebox.input.Base) and value
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

	def set_returnvalue(self,value):
		assert value==None or isinstance(value,tuple)
		if value==None:
			self._returnvalue = (None,None)
		else:
			self._returnvalue = value
	def get_returnvalue(self):
		return self._returnvalue
	returnvalue = property(get_returnvalue,set_returnvalue)

	""" Private methods """
	def _ffmpeg_output(self,process):
		line = process.stderr.readline()
		while line:
			m = re.match(r"\s*frame=\s*(\S+)\s+fps=\s*(\S+)\s+q=(\S+)\s+size=\s*(\S+)\s+time=\s*(\S*)\s+bitrate=\s*(\S*)",line)
			if m:
				self._queue.put({
					"stderr": line.strip(),
					"frame": long(m.group(1)),
					"fps": float(m.group(2)),
					"q": float(m.group(3)),
					"size": m.group(4),
					"time": m.group(5),
					"bitrate": m.group(6)
				})
			else:
				self._queue.put_nowait({
					"stderr": line.strip()
				})
			line = process.stderr.readline()
		""" Add in a terminating value to indicate the end of the queue """
		self._queue.put(None)

	def _ffmpeg_thread(self,*flags):
		logging.debug("execute: %s %s" % (self._ffmpeg," ".join(flags)))
		proc = subprocess.Popen(
			"%s %s" % (self._ffmpeg," ".join(flags)),
			shell=True,
			universal_newlines=True,
			stderr=subprocess.PIPE
		)
		stderr_thread = threading.Thread(target=self._ffmpeg_output,args=(proc,))
		stderr_thread.daemon = True
		stderr_thread.start()
		
		# wait for subprocess to complete
		status = None
		while True:
			try:
				""" Get queue item, break after 500ms """
				item = self._queue.get(True,0.5)
				""" If empty item, then break out of the loop """
				if not item: break

				""" Set status """
				if isinstance(item,dict):
					status = item.get("stderr")

				""" Debug """
				logging.debug("Status: %s" % item)

			except Queue.Empty:
				pass
	
		returncode = proc.poll()
		if returncode:
			self.returnvalue = (returncode,status)
		else:
			self.returnvalue = (returncode,None)
		self.input = None

	def _flags_input_audio(self,control):
		assert isinstance(control,Control)
		return util.get_flags_for_audio(control.audio)

	def _flags_output(self,control):
		assert isinstance(control,Control)
		return [
			"-c:v copy","-b:v %s" % control.bitrate,"-c:a aac","-b:a %s" % constants.STREAMER_AUDIO_BITRATE,
			"-map 0:0","-map 1:0","-strict experimental",
			"-f flv"
		]
	
	def _get_video_input(self,filename,control):
		assert isinstance(control,Control)
		if control.video=="picamera":
			return livebox.input.Camera(filename,control)
		if control.video=="file":
			return livebox.input.File(filename,control)
		raise Error("Invalid video input method")

	def start(self,filename,control):
		assert isinstance(filename,basestring) and filename
		assert os.path.exists(filename)
		assert isinstance(control,Control)

		""" Get parameters """
		if self.running:
			raise Error("Invalid state")
		if not control.url:
			raise Error("Invalid URL: %s" % control.url)
		
		# Open input source
		self.input = self._get_video_input(filename,control)

		# Flags for streamer
		flags = [ ]
		flags.extend(self._flags_input_video(control))
		flags.extend(self._flags_input_audio(control))
		flags.extend(self._flags_output(control))
		flags.append(control.url)
	
		# create background thread to stream
		t = threading.Thread(target=self._ffmpeg_thread,args=flags)
		t.daemon = True
		t.start()
	
	def stop(self):
		# TODO: Send signal 2 to ffmpeg
		pass

