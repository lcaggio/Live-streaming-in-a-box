#!/bin/bash
FIFO_FILE="${HOME}/video.h264.fifo"
WIDTH=640
HEIGHT=360
KBPS=750
FPS=25
STREAM_NAME="djt.zepf-h0qx-1z8d-821q"
STREAM_URL="rtmp://a.rtmp.youtube.com/live2/${STREAM_NAME}"
GOP_SIZE=`python -c "print ${FPS}*2"`

FFMPEG_BINARY_LOCAL="${HOME}/bin/ffmpeg"
FFMPEG_BINARY_SYSTEM="/usr/bin/ffmpeg"

# Set up fifo
rm -fr "${FIFO_FILE}"
mkfifo "${FIFO_FILE}"

# Start camera capture in background
raspivid -n -t 86400000 -fps ${FPS} -g ${GOP_SIZE} -w ${WIDTH} -h ${HEIGHT} -b ${KBPS}000 -pf main -ih -o "${FIFO_FILE}" &

# Stream in foreground
${FFMPEG_BINARY_LOCAL} \
  -f h264  -r ${FPS} -i "${FIFO_FILE}" \
  -re \
  -f lavfi -i "sine=frequency=1000:duration=0" \
  -c:v copy -b:v ${KBPS}k -c:a aac -b:a 64k \
  -map 0:0 -map 1:0  -strict experimental \
  -f flv "${STREAM_URL}"

# Use this for empty audio
#    -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero
# Use this for sine wave
#    -f lavfi -i "sine=frequency=1000:duration=0"







