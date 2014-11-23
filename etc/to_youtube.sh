#!/bin/bash

FIFO_FILE="camera.fifo"
WIDTH=854
HEIGHT=480
KBPS=200
FPS=5
STREAM_NAME="djt.zepf-h0qx-1z8d-821q"
STREAM_URL="rtmp://a.rtmp.youtube.com/live2/${STREAM_NAME}"

# Stream in foreground
avconv \
	-f h264 -b:v 1000 -r ${FPS} -i ${FIFO_FILE} -codec:v copy \
	-f s16le -ar 44100 -ac 2 -i /dev/zero -codec:a aac -b:a 64k \
	-f flv -strict experimental "${STREAM_URL}"

