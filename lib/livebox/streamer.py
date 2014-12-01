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
from . import constants

################################################################################
# Streamer class

class Streamer(object):
	def __init__(self,ffmpeg=None):
		assert isinstance(ffmpeg,basestring) and ffmpeg
		assert os.path.exists(ffmpeg) and os.path.isfile(ffmpeg)
		self._ffmpeg = ffmpeg
		self.running = False
		self._queue = Queue.Queue()
	
	""" Private methods """
	def _ffmpeg_output(self,process):
		logging.info("_ffmpeg_output started")
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
		logging.info("_ffmpeg_output terminating")

	def _flags_input_audio(self):
		return [ ]

	def _flags_input_video(self):
		return [ "-re","-f %s" % constants.CAMERA_FORMAT,"-r %s" % framerate,"-i \"%s\"" % filename ]

	def _flags_output(self):
		return [
			"-c:v copy","-b:v %s" % bitrate,"-c:a aac","-b:a %s" % constants.STREAMER_AUDIO_BITRATE,
			"-map 0:0","-map 1:0","-strict experimental",
			"-f flv"
		]

	def start(self,video=None,audio=None,framerate=None,bitrate=None,url=None):
		assert isinstance(filename,basestring) and filename
		assert os.path.exists(filename)
		assert isinstance(framerate,(int,long)) and framerate > 0
		assert isinstance(bitrate,(int,long)) and bitrate > 0
		assert isinstance(url,basestring) and url
	
		flags = [ ]
		flags.extend(self._flags_input_video(filename,framerate))
		flags.extend(self._flags_input_audio(audio))
		flags.extend(self._flags_output())
	
	def stop(self):
		pass

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
