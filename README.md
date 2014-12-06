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


Current Status
--------------

As of 3 Dec 2014:

  * For the command-line usage, this needs to be updated so it currently no
    not working.
  * For the server usage, the `lib/livebox/streamer.py` and `lib/livebox/camera.py`
    modules need to be completed. The server version is therefore still under
	development.
	
Further information is provided in the NOTES


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

The server-version of the software provides a way to stream from the Raspberry Pi
via non-command line interfaces. The way to start the server version is (for
example) as follows:

```
 python src/webserver.py --port 8000
```

The server can be bound to the local interface (thus preventing access via the
network) or to a particular network interface. The command line switches are as
follows:

  * `--port 8000` Optional. Set the port number to listen for incoming connections on.
  
  * `--bind * | localhost` Optional. Listen to all interfaces or only some 
    interfaces. By setting this to `localhost` you can ensure that only 
	processes on the device itself can send API commands.
	
  * `--wwwdocs <folder>` You can set a custom folder to use as the static files
    that can be served by the server. In general, you won't want to set this.
	
  * `--ffmpeg <exec>` Optional. You can set the ffmpeg binary to be used for 
    encoding and streaming.

  * `--verbose` Reports more information on the console than usual, for debugging
    purposes.

The API format for version 1 is as follows:

   * `GET /api/v1/status` Returns a JSON structure which reports the current
	 status of the livebox. It reports whether the streamer is on or off, and the CPU
	 and network loads.

   * `GET /api/v1/shutdown` Stops the server and returns to the command prompt.
	 
   * `GET|PUT|POST /api/v1/control` Get control data for the current live stream,
	 or alter the parameters.
	 
   * `GET /api/v1/(start|stop)` Start or stop streaming
   
There is no security considered yet. Ideally, we can introduce some sort of authentication
later. This would be important due to the potentially sensitive nature of what is being
streamed!

Here is what the current status response might look like:

```
{
  "product": "com.youtube.livebox",
  "version": "1.0",
  "name": "rpi2.nw1", // hostname or name set otherwise
  "timestamp": XXXX,  // system time
  "id": "XXXXXXXXX",  // MAC address
  "status": "idle",   // idle, preparing, running, stopping
  "cpu": 32.0,        // CPU percentage used by the software
  "disk": 76.0,       // Temporary storage used in percentage
  "net": 290000       // Outgress in bytes
}
```

Here is what a control message looks like:

```
{
    "timestamp": XXXX, // time of last update
	"url": "rtmp://a.rtmp.youtube.com/live2/djt.zepf-h0qx-1z8d-821q",
	"resolution": "360p",
	"bitrate": 100000,
	"video": "picamera",
	"audio": "1kHz",
	"fps": 25,
	"quality": null,  // use default
	"hflip": false,   // horizonal image flip
	"vflip": false    // vertical image flip
}
```

You can POST or PUT control data or GET it. In either case, it will return the
control data back again. To start or stop the streaming, GET that, and
it will return a OK or Bad Request status depending on whether that's possible.

There is also a generic webserver which will return anything under the document
root, as long as the files fetched aren't under the "api" namespace.

License
-------

Copyright 2014-2015 Google Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this 
file except in compliance with the License. You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
ANY KIND, either express or implied. See the License for the specific language governing
permissions and limitations under the License.

