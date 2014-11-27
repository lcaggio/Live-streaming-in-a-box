#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Live Streaming in a Box
    -----------------------
	Constants for livebox
"""
__author__ = "davidthorpe@google.com (David Thorpe)"

""" Default camera resolutions and bitrates """
CAMERA_RESOLUTION = (
	("360p",640,360,"750kbps"),
	("240p",426,240,"400kbps"),
	("480p",854,480,"1000kbps"),
	("720p",1280,720,"2500kbps"),
	("1080p",1920,1080,"4500kbps"),
)

""" Other constants which shouldn't be changed """
CAMERA_PROFILE = ("main","high","baseline","constrained") # first is the default
CAMERA_FORMAT = "h264"
CAMERA_FRAMERATE = 25
CAMERA_QUALITY = None

""" Streamer constants """
STREAMER_EXEC = "bin/ffmpeg"
STREAMER_AUDIO = (
	("1kHz","-f lavfi","-i \"sine=frequency=1000:duration=0\""),
	("silence","-ar 44100","-ac 2","-acodec pcm_s16le","-f s16le","-ac 2","-i /dev/zero"),
)
STREAMER_AUDIO_BITRATE = "64k"

""" FIFO NAME """
FIFO_NAME = "camera.h264.fifo"

""" Network constants """
NETWORK_BIND = "*"
NETWORK_PORT = 8080
NETWORK_BASEPATH_API = "/api/"

""" HTTP Status codes """
HTTP_STATUS_OK = 200
HTTP_STATUS_NOCONTENT = 204
HTTP_STATUS_BADREQUEST = 400
HTTP_STATUS_NOTFOUND = 404
HTTP_STATUS_AUTHREQUIRED = 401
HTTP_STATUS_SERVERERROR = 500

""" Mimetypes """
HTTP_INDEX_FILENAME = "index.html"
HTTP_MIMETYPES = (
	("","application/octet-stream"), # Default
	(".html","text/html"),
	(".txt","text/plain"),
	(".css","text/css"),
	(".js","application/javascript"),
	(".json","application/json"),
	(".png","image/png"),
	(".jpg","image/jpeg"),
	(".gif","image/gif"),
	(".ico","image/x-icon"),
)

