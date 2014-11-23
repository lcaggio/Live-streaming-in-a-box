Live-streaming-in-a-box
=======================

Description
-----------

This is a package to live stream from your Raspberry Pi and Camera to YouTube,
which can be controlled from a web-based interface, essentially turning your 
Raspberry Pi into a "Livestreaming in a Box" solution!

Prerequisite
------------

 * A Raspberry Pi + Pi Cam
 * Internet connection (wifi or ethernet)
 * The Raspian operating system (probably) with Python 2.7 and picamera installed

Installation
------------

Usage
-----

There is a command line python program called "stream.py" which can be used
to stream directly from your camera to YouTube. You can use this as follows:

```
 python src/stream.py --resolution 360p rtmp://a.rtmp.youtube.com/live2/djt.zepf-h0qx-1z8d-821q
```

In this example, you stream from the camera to a YouTube stream using the 360p
resolution. The command line arguments are as follows, with some examples:

  * `--verbose` Will show more output on the console
  * `--resolution 240p | 360p | 480p | 720p | 1080p` The resolution of the broadcast to send
  * `--audio silence | 1kHz` Whether to send a 1kHz tone or silence as the audio track
  * `--fps 15 | 25 | 30` The framerate to use
  * `--bitrate 800kpbs | 1M | 100000` The bitrate to use
  
The only required argument is the URL, but it's also worth setting the resolution
argument to ensure you're sending the right quality.

