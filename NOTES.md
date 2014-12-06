Live-streaming-in-a-box
=======================

TODO
----

Other things to consider:

  * Want to be able to store logs and data in an sqlite database, which can be
    accessed and analysed later, via the API
  * Authorization and authentication to be done in the API for network connections,
    probably not so necessary on the localhost interface.
  * Have a reliable channel for accessing the remote location to pull down commands
    and return responses. Look here for example: http://schibum.blogspot.co.uk/2011/06/using-google-appengine-channel-api-with.html
	We should probably use the XMPP standard or something to get and send messages.
  * Want to be able to output to a file on temporary storage, or loop video/audio input from
    a file in temporary storage for output.

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

