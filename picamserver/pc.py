#! /usr/bin/env python3

"""
picamserver.py

Raspberry Pi camera server for exposing camera module over http.

Perry Tobin expanded code from 

(c) David Palmer
This code licensed under GPLv2
Started 2013-09-11

A similar project is BerryCam from fotosynlabs, which talks to
an iPad Application.  See
https://bitbucket.org/fotosyn/fotosynlabs.git

"""

from __future__ import print_function

import logging
logging.basicConfig(level=logging.DEBUG)

import sys
import os
import argparse
import re
import subprocess
import signal

if sys.version_info.major == 2 :
    logging.warning("Python 3 is prefered for this program")
    import urlparse
    import SimpleHTTPServer as httpserver
    import SocketServer as socketserver
else :
    import urllib.parse as urlparse
    import http.server as httpserver
    import socketserver

defaultPort = 8003  # Change here or use the --port argument
defaultFileroot = os.path.dirname(__file__) # change here or use --fileroot argument

class PiCamHandler(httpserver.SimpleHTTPRequestHandler):
    raspiPath = "/usr/bin/raspistill"
    # Take the help output and convert it to this by 
    # ^-([a-z]+), *--([a-z]+)\s:\s*(.*)$  ---> ['\2', '\1'],     # \3
    argnames = [    # Arguments to raspistill, first as long form, then as short
            ['help', '?'],       # This help information
            ['width','w'],      # Set image width <size>
            ['height', 'h'],     # Set image height <size>
            ['quality', 'q'],     # Set jpeg quality <0 to 100>
            ['raw', 'r'],     # Add raw bayer data to jpeg metadata
            ['output', 'o'],     # Output filename <filename> (to write to stdout, use '-o -'). If not specified, no file is saved
            ['latest', 'l'],     # Link latest complete image to filename <filename>
            ['verbose', 'v'],     # Output verbose information during run
            ['timeout', 't'],     # Time (in ms) before takes picture and shuts down (if not specified, set to 5s)
            ['thumb', 'th'],     # Set thumbnail parameters (x:y:quality)
            ['demo', 'd'],     # Run a demo mode (cycle through range of camera options, no capture)
            ['encoding', 'e'],     # Encoding to use for output file (jpg, bmp, gif, png)
            ['exif', 'x'],     # EXIF tag to apply to captures (format as 'key=value')
            ['timelapse', 'tl'],     # Timelapse mode. Takes a picture every <t>ms
            ['fullpreview', 'fp'],     # Run the preview using the still capture resolution (may reduce preview fps)
            ['preview', 'p'],     # Preview window settings <'x,y,w,h'>
            ['fullscreen', 'f'],     # Fullscreen preview mode
            ['opacity', 'op'],     # Preview window opacity (0-255)
            ['nopreview', 'n'],     # Do not display a preview window
            ['sharpness', 'sh'],     # Set image sharpness (-100 to 100)
            ['contrast', 'co'],     # Set image contrast (-100 to 100)
            ['brightness', 'br'],     # Set image brightness (0 to 100)
            ['saturation', 'sa'],     # Set image saturation (-100 to 100)
            ['ISO', 'ISO'],     # Set capture ISO
            ['vstab', 'vs'],     # Turn on video stablisation
            ['ev', 'ev'],     # Set EV compensation
            ['exposure', 'ex'],     # Set exposure mode (see Notes)
            ['shutter', 'ss'],  # set shutter speed in microseconds
            ['awb', 'awb'],     # Set AWB mode (see Notes)
            ['imxfx', 'ifx'],     # Set image effect (see Notes)
            ['colfx', 'cfx'],     # Set colour effect (U:V)
            ['metering', 'mm'],     # Set metering mode (see Notes)
            ['rotation', 'rot'],     # Set image rotation (0-359)
            ['hflip', 'hf'],     # Set horizontal flip
            ['vflip', 'vf'],     # Set vertical flip
            ['drc', 'drc'],
            ['roi', 'roi'],     # Set region of interest (x,y,w,d as normalised coordinates [0.0-1.0])
            ]
    # Which arguments are flags (i.e. that don't take the next command line argument
    # use flag=0 or flag=1 in the URL to set or reset
    flagargs = ['help','raw','verbose','demo','fullpreview','fullscreen','nopreview','vstab','hflip','vflip']
    short2long = dict([(s,l) for l,s, in argnames])
    defaultargs = {'output':'-','rotation':'90','timeout':'500','nopreview':'1','vflip':'1','hflip':'1','fullscreen':'1','exposure':'auto', 'awb':'auto'}
    
    def do_GET(self) :
        logging.info("GET request: %s" % (self.path,))
        parsedParams = urlparse.urlparse(self.path)
        queryParsed = urlparse.parse_qs(parsedParams.query)
        logging.debug("parsedParams: %s" % (parsedParams,))
        logging.debug("queryParsed: %s" % (queryParsed,))
        if (parsedParams.path == "/") :
            path = "/file/pi-default.html"
        else :
            path = parsedParams.path
        splitpath = os.path.split(path)
        logging.debug("splitPath = %s" % (splitpath,))
        
        #
        # "/check"
        #
        if parsedParams.path == "/check" :
            self.send_response(200)
            resp = "<html><head><body>not used</body></head></html>" 
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(resp,"UTF-8"))
        #
        # Admin parameters - { TODO }
        #
        elif parsedParams.path == "/admin" :

            # Check for files
            #with open("/home/pi/rpispy/rpispy_vcu/config.py") as f:
            #  for ln in f:
            #    logging.debug(ln)

            self.send_response(200)
            s = subprocess.check_output(["free","-m"])
            t = subprocess.check_output(["/opt/vc/bin/vcgencmd","measure_temp"])
            u = subprocess.check_output(["uptime"])
            #temp = float(s.split(bytes('=',"UTF-8"))[1][:-3])
            lines = s.split(bytes('\n', "UTF-8"))             
            resp = "<html><head><body>Admin:<br>%s" % str(lines[0])[3:-1]
            resp += "<br>%s" % str(lines[1])[2:-1]
            resp += "<br>%s" % str(lines[2])[2:-1]
            resp += "<br>Temp:%s" % str(t)[7:-3]
            resp += "<br>Uptime: %s" % str(u)[3:-3]
            resp += "</body></head></html>"
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(resp,"UTF-8"))
        #
        # "/live"
        #
        elif parsedParams.path == "/live" :
            self.send_response(200)             
            resp = "Encoder process called"  
            path = "live.html"
            self.send_header("Access-Control-Allow-Origin", "*")
            logging.debug("/home/pi/live.sh %s &" % queryParsed['id'][0])
            subprocess.call("/home/pi/live.sh %s &" % (queryParsed['id'][0]), shell=True)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(resp,"UTF-8"))
        #
        # "/kill"
        #
        elif parsedParams.path == "/kill" :
            #path = "/file/kill.html"
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            resp = "<html><head><body>Stream killed.</body></head></html>"
            subprocess.call("/home/pi/picamserver/kill.sh", shell=True)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(resp,"UTF-8"))
        #
        # "/camera"
        #
        elif parsedParams.path == "/camera" : 
            # Code 304 Not Modified could be used for too-rapid image requests
          
            self.image,self.diagnostic = self.runCommand(queryParsed)
            self.send_response(200)
            self.send_header("Content-type", "image/jpeg")
            self.send_header("Content-length", len(self.image))
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Expires","Thu, 01 Dec 1994 16:00:00 GMT")
            self.end_headers()
            self.wfile.write(self.image)
        #
        # "/file"
        #
        elif splitpath[0] == '/file' :
            if len(splitpath) > 2 :
                raise RuntimeError("Only one directory level allowed")
            filename = os.path.join(defaultFileroot,splitpath[1])
            self.send_response(200)
            #self.send_header("Content-type", self.guess_type(filename))
            self.end_headers()
            self.wfile.write(open(filename,"rb").read())
        else :
            self.send_error(501,"Only /camera request is supported now")
            #path = ".." + splitpath


    def runCommand(self, queryParsed) :
        """From the parsed params, make and execute the RaspiStill command line"""
        # Convert URL to a dict of args
        args = self.defaultargs.copy()
        residual_args = {}
        for arg,value in queryParsed.items() :
            if arg in self.short2long :
                args[self.short2long[arg]] = value[0]
            else :
                # IMPROVEME, allow unique prefixes
                if arg in self.short2long.values() :
                    args[arg] = value[0]
                else :
                    residual_args[arg] = value
        if args['output'] != '-' or 'latest' in args :
            raise RuntimeError("File output not yet supported")
        # Convert dict of args to a command line array
        cmd = [self.raspiPath]
        for arg,value in args.items() :
            if arg in self.flagargs :
                if value == '1' :
                    cmd.append('--'+arg)    # Add the flag
            else :
                cmd.append('--'+arg)
                cmd.append(value)
        logging.info("Raspistill command is broken down as %s" % (cmd,))
        if residual_args :
            logging.info("Unused arguments are: %s" % (residual_args,))
        # FIXME doesn't return verbose output and other diagnostics yet
        image = subprocess.check_output(cmd,stderr=sys.stderr)
        return (image,"unused args: %s" % (residual_args,)) 
        
                
    def sanitizeFile(self, filename) :
        """Make sure the filename isn't toxic"""
        if re.findall("(\.\.)|(^~)",filename) :
            logging.critical("IP : %s tried to write to file %s.\n" 
                            "Full GET: %s\n"
                            "I no longer feel safe and am shutting down." 
                                % (self.client_address[0], filename,self.path))
            raise RuntimeError("Attempted file system violation")
    
def main(argv) :
    httpd = socketserver.TCPServer(("", defaultPort), PiCamHandler)
   
    logging.info("picamserver -- Listening on port %d", defaultPort)
    httpd.serve_forever()



if __name__ == "__main__" :
    main(sys.argv)
