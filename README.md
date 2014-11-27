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

The server-version of the software provides a way to stream from the Raspberry Pi
via non-command line interfaces. The way to start the server version is (for
example) as follows:

```
 python src/webserver.py --port 8000
```

The server can be bound to the local interface (thus preventing access via the
network) or to a particular network interface. The command line switches are as
follows:

  * `--port 8000` Set the port number to listen for incoming connections on
  
  * `--bind * | localhost` Listen to all interfaces or only some interfaces. By
    setting this to `localhost` you can ensure that only processes on the device
	itself can send API commands.
	
  * `--wwwdocs <folder>` You can set a custom folder to use as the static files
    that can be served by the server. In general, you won't want to set this.

  * `--verbose` Reports more information on the console than usual, for debugging
    purposes.

The API format for version 1 is as follows:

   * `GET /api/v1/status` Returns a JSON structure which reports the current
	 status of the livebox. It reports whether the streamer is on or off, and the CPU
	 and network loads.

   * `GET /api/v1/shutdown` Stops the server and returns to the command prompt.
	 
   * `GET|POST /api/livebox/v1/control` TODO Get control data for the current live stream,
	 or alter the parameters.
	 
   * `PUT /api/livebox/v1/(start|stop)` TODO Start or stop streaming
   
There is no security considered yet. Ideally, we can introduce some sort of authentication
later. This would be important due to the potentially sensitive nature of what is being
streamed!

Here is what the current status response might look like:

```
{
  "product": "com.youtube.livebox",
  "version": "1.0",
  "name": "rpi2.nw1", // hostname or name set otherwise
  "id": "XXXXXXXXX",  // MAC address
  "status": "idle",   // idle, preparing, streaming, stopping
  "cpu": 32.0,        // CPU percentage used by the software
  "disk": 76.0,       // Temporary storage used in percentage
  "net": 290000       // Outgress in bytes
}
```

Here is what a control message looks like:

```
{
	"name": "djt.zepf-h0qx-1z8d-821q",
	"url": "rtmp://a.rtmp.youtube.com/live2",
	"resolution": "360p",
	"bitrate": 100000,
	"audio": "1kHz",
	"fps": 25,
	"quality": null // use default
}
```

You can POST control data or GET it. In either case, it will return the
control data back again. To start or stop the streaming, PUT that, and
it will return a OK or Bad Request status depending on whether that's possible.

There is also a generic webserver which will return anything under the document
root, as long as the files fetched aren't under the "api" namespace.

TODO
----

Other things to consider:

  * Want to be able to store logs and data in an sqlite database, which can be
    accessed and analysed later, via the API
  * Authorization and authentication to be done in the API for network connections,
    probably not so necessary on the localhost interface.
  * Have a reliable channel for accessing the remote location to pull down commands
    and return responses. Look here for example: http://schibum.blogspot.co.uk/2011/06/using-google-appengine-channel-api-with.html
	

TEMP
----
Solution with 2 wifi adapters. 
 - wlan1: fixed SSID to always access the pi and configure wlan0
 - wlan0: configurable wifi
To use the UI, you need to:
 - apt-get install lighttpd php5-cgi
 - sudo lighty-enable-mod fastcgi-php
 - /etc/init.d/lighttpd restart
 - Add to /etc/sudoers the following: www-data ALL=(ALL) NOPASSWD:/sbin/ifdown wlan0,/sbin/ifup wlan0,/bin/cat /etc/wpa_supplicant/wpa_supplicant.conf,/bin/cp /tmp/wifidata /etc/wpa_supplicant/wpa_supplicant.conf,/sbin/wpa_cli scan_results,/sbin/wpa_cli scan

Inspired by: http://sirlagz.net/2013/02/06/script-web-configuration-page-for-raspberry-pi/

