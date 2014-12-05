#!/bin/bash

#sudo python /home/pi/PiGlow/live-leds.py &

echo $1
url="rtmp://a.rtmp.youtube.com/live2/$1"
fifo="/home/pi/live.fifo.h264.youtube"

rm -f "$fifo"
mkfifo "$fifo"

#this uses the patched version of raspivid with infinite time and -g option
raspivid \
 -fps 25 -g 50 \
 -vf -hf \
 -w 1280 -h 720 \
 -t 0 -b 2500000 -o "$fifo" &

/usr/bin/ffmpeg \
 -i "$fifo" \
 -f s16le \
 -i /dev/zero \
 -vcodec copy \
 -acodec aac \
 -r 50 \
 -b:v 4M \
 -g 50 \
 -s 1280x720 \
 -keyint_min 50 \
 -ac 2 \
 -ar 44100 \
 -ab 128k \
 -f h264 \
 -strict experimental \
 -c:v copy \
 -f flv $url
