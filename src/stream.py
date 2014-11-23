#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Command-line interface to stream to YouTube
	
	Usage: stream.py <flags>
"""

__author__ = "davidthorpe@google.com (David Thorpe)"

# python imports
import os,sys,logging

# add python libraries:
# 'lib' for shared modules
# 'third_party' for external (third party) modules
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
code_paths = [
	os.path.join(root_path,'lib'),
	os.path.join(root_path,'third_party')
]
for path in code_paths:
	if (path not in sys.path) and os.path.exists(path): sys.path.insert(0,path)

# Python imports
import time

# Third party imports
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_recording('foo.h264')
    camera.wait_recording(60)
    camera.stop_recording()

