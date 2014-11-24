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


Design
------

Two versions of the software in development - a command-line version and
a server-based version which exposes the streamer as an API which can be
controller remotely. There would be then several UI interfaces:

  * A web-based javascript interface that can be launched from the box
    itself
  * A "on box" interface which allows the box to be controlled from a
    hardware touch-screen
  * A remote control interface which allows the box to be controlled in
    batch by a cloud-based web interface


Installation
------------

TODO


Command Line Usage
------------------

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
  * `--quality 10 | 20 | 30 | 40` Set the camera quality
  
The only required argument is the URL, but it's also worth setting the resolution
argument to ensure you're sending the right quality.

Server Usage
------------

TODO

The server-version of the software needs to be installed instead of the command-line
version. The way to start the server version is as follows:

```
 python src/server.py --bind localhost --port 8000 --mdns --docroot <document root>
```

The server can be bound to the local interface (thus preventing access via the
network) or to a particular network interface. You set the port to listen to API
incoming commands. The API format for version 1 is as follows:

   * `GET /api/livebox/v1/status` Returns a JSON structure which reports the current
	 status of the livebox. It reports whether the streamer is on or off, and the CPU
	 and network loads.
	 
   * `GET|POST /api/livebox/v1/control` Get control data for the current live stream,
	 or alter the parameters.
	 
   * `PUT /api/livebox/v1/(start|stop)` Start or stop streaming
   
There is no security considered yet. Ideally, we can introduce some sort of authentication
later. This would be important due to the potentially sensitive nature of what is being
streamed!


