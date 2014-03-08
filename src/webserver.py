#!/usr/bin/python

"""
	Usage: webserver.py <flags>
"""

# python imports
import os,sys,json,threading,webbrowser

# add python libraries:
src_path = os.path.abspath(os.path.dirname(__file__))
code_paths = [
	os.path.join(src_path,'..','lib')
]
for path in code_paths:
	if (path not in sys.path) and os.path.exists(path): sys.path.insert(0,path)

# Google API imports
import gflags
from oauth2client import client as oauth2_client
from oauth2client import file as oauth2_file
from oauth2client import tools as oauth2_tools

# local imports
from livebox import webserver, api

# constants
ROOT_PATH = os.path.join(src_path,"..")
CLIENT_SECRETS_FILE = os.path.join(ROOT_PATH,"etc","client_secrets.json")
TOKEN_STORAGE = os.path.join(ROOT_PATH,"etc","oauth2.json")
WEBROOT_PATH = os.path.normpath(os.path.join(ROOT_PATH,"etc","www"))
MIMETYPES_PATH = os.path.join(ROOT_PATH,"etc","mime.types")
YOUTUBE_SCOPES = [
	"https://www.googleapis.com/auth/youtube",
	"https://www.googleapis.com/auth/youtubepartner"
]

# command line flags
FLAGS = gflags.FLAGS
gflags.DEFINE_string('address','localhost',"IP Address to bind on")
gflags.DEFINE_integer('port',8000,"Port")
gflags.DEFINE_integer('debug',None,"Debug Level")

# return credentials - from file or authorize
def get_credentials(scopes):
	flow = oauth2_client.flow_from_clientsecrets(CLIENT_SECRETS_FILE,scope=scopes)
	storage = oauth2_file.Storage(TOKEN_STORAGE)
	credentials = storage.get()
	if credentials is None or credentials.invalid:
		credentials = oauth2_tools.run(flow, storage)
	return credentials

# Request Processor
class RequestHandler(webserver.RequestHandler):	
	# METHODS
	def get_broadcasts(self):
		self.response_json(self.server.youtube.run_broadcasts({ }))
	def get_streams(self):
		self.response_json(self.server.youtube.run_streams({ }))
	# ROUTES
	routes = (
		(webserver.RequestHandler.METHOD_GET,r"^/api/broadcast$",get_broadcasts),
		(webserver.RequestHandler.STATIC,r"^.*$"),
	)

# main method
def main(argv):
	try:
		argv = FLAGS(argv)
		if len(argv) != 1:
			raise gflags.FlagsError("Invalid arguments, use --helpshort for help")
		if FLAGS.debug:
			httplib2.debuglevel = FLAGS.debug

		# get authentication credentials
		credentials = get_credentials(YOUTUBE_SCOPES)
		if credentials==None or credentials.invalid:
			raise gflags.FlagsError("Unable to get credentials")

		# create server
		server = webserver.ThreadedHTTPServer((FLAGS.address,FLAGS.port),RequestHandler,WEBROOT_PATH,MIMETYPES_PATH)
		server.youtube = api.Service(credentials)

		# Open web browser
		print "HTTP Server Running: http://%s:%s/" % (FLAGS.address,FLAGS.port)
		webbrowser.open_new_tab("http://%s:%s/" % (FLAGS.address,FLAGS.port))
		
		# Wait
		server.serve_forever()		
	except KeyboardInterrupt:
		# Exit success
		server.socket.close()
		sys.exit(0)
	except gflags.FlagsError, e:
		print "Usage error: %s" % e
		sys.exit(-1)

# call main method
if __name__ == "__main__":
	main(sys.argv)
