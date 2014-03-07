#!/bin/bash

url="rtmp://a.rtmp.youtube.com/live2/<STREAM NAME HERE>"
fifo="live.fifo.h264.youtube"

rm -f "$fifo"
mkfifo "$fifo"

#this uses the patched version of raspivid with infinite time and -g option
raspivid \
 -fps 25 -g 50 \
 -w 1280 -h 720 \
 -t 0 -b 500000 -o "$fifo" &

ffmpeg -y \
 -i "$fifo" \
 -f s16le \
 -i /dev/zero \
 -vcodec copy \
 -acodec libfaac \
 -r 25 \
 -b:v 4M \
 -g 50 \ -s 1280x720 \
 -keyint_min 50 \
 -ac 2 \
 -ar 44100 \
 -ab 64k \
 -vb 500k \
 -c:v copy \
 -f flv $url
