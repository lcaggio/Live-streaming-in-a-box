#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python imports
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import urlparse,socket,os,logging,json
import datetime

# local imports
from . import constants

################################################################################

class Error(Exception):
	def __init__(self,reason,code=constants.HTTP_STATUS_SERVERERROR):
		assert isinstance(reason,basestring) and reason
		assert isinstance(code,(int,long)) and code
		Exception.__init__(self,reason)
		self._reason = reason
		self._code = code
	
	@property
	def reason(self):
		return self._reason
	@property
	def code(self):
		return self._code
	def __str__(self):
		return "%s (Error: %s)" % (self.reason,self.code)

################################################################################

class Server(HTTPServer):
	def __init__(self,bind,port,wwwroot):
		assert isinstance(bind,basestring)
		assert isinstance(port,(int,long)) and port > 0
		assert isinstance(wwwroot,basestring) and os.path.isdir(wwwroot)

		try:
			HTTPServer.__init__(self,(bind,port),APIRequest)
		except socket.error, e:
			raise Error("Server bind error: %s" % e)

		self.running = False
		self.wwwroot = wwwroot
		self.mimetypes = dict(constants.HTTP_MIMETYPES)
	
	""" PROPERTIES """
	def set_running(self,value):
		assert isinstance(value,bool)
		self._running = value
	def get_running(self):
		return self._running
	running = property(get_running,set_running)
	
	def set_wwwroot(self,value):
		assert isinstance(value,basestring) and value and os.path.isdir(value)
		self._wwwroot = value
	def get_wwwroot(self):
		return self._wwwroot
	wwwroot = property(get_wwwroot,set_wwwroot)
	
	
	""" METHODS """
	def get_mimetype(self,filename):
		(r,ext) = os.path.splitext(filename)
		return self.mimetypes.get(ext,self.mimetypes.get(""))
	
	def run(self):
		self.running = True
		while self.running:
			self.handle_request()

################################################################################

class Request(BaseHTTPRequestHandler):

	METHOD_GET = 1
	METHOD_PUT = 2
	METHOD_POST = 3
	METHOD_DELETE = 4
	
	def handler(self,method,path):
		self.json_response = False # Normal error response
		
		""" Only allow GET requests """
		if method != Request.METHOD_GET:
			raise Error("Bad request: %s" % path.path,constants.HTTP_STATUS_BADREQUEST)
		""" Handle static files """
		absolute_path = os.path.normpath(os.path.join(self.server.wwwroot,path.path.strip('/')))
		if not absolute_path.startswith(self.server.wwwroot):
			raise Error("Bad request: %s" % path.path,constants.HTTP_STATUS_BADREQUEST)
		if not os.path.exists(absolute_path):
			raise Error("Not Found: %s" % path.path,constants.HTTP_STATUS_NOTFOUND)

		""" Deal with index files """
		if os.path.isfile(absolute_path):
			pass
		elif os.path.isdir(absolute_path):
			absolute_path = os.path.join(absolute_path,constants.HTTP_INDEX_FILENAME)

		""" Don't allow hidden files, get mimetype """
		(_,filename) = os.path.split(absolute_path)
		if filename.startswith("."):
			raise Error("Bad request: %s" % path.path,constants.HTTP_STATUS_BADREQUEST)
		mimetype = self.server.get_mimetype(filename)

		""" Do logging """
		logging.debug("%s => filename: %s mimetype: %s" % (path.path,filename,mimetype))

		""" Send static file response """
		self.send_response(200)
		self.send_header('Content-type',mimetype)
		self.send_header('Date', self.date_time_string())
		self.send_header('Last-Modified',self.date_time_string(os.stat(absolute_path).st_mtime))
		self.end_headers()
		try:
			with open(absolute_path,"rb") as filehandle:
				self.wfile.write(filehandle.read())
		except IOError, e:
			raise Error("IOError")

	def send_error(self,code,reason):
		if not self.json_response:
			return BaseHTTPRequestHandler.send_error(self,code,reason)
		self.send_response(code)
		self.send_header('Content-type',"application/json")
		self.end_headers()
		self.wfile.write(json.dumps({
			"code": code,
			"reason": reason
		}))
		self.wfile.write("\n")

	def do_POST(self):
		try:
			return self.handler(Request.METHOD_POST,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)
	def do_PUT(self):
		try:
			return self.handler(Request.METHOD_PUT,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)
	def do_DELETE(self):
		try:
			return self.handler(Request.METHOD_DELETE,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)
	def do_GET(self):
		try:
			return self.handler(Request.METHOD_GET,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)

################################################################################

class APIRequest(Request):

	def get_route(self,method,path):
		for route in APIRequest.ROUTES:
			assert isinstance(route,tuple) and len(route)==3
			if method != route[0]: continue
			if path != route[1]: continue
			return route[2]
		return None

	def handler(self,method,path):
		if not path.path.startswith(constants.NETWORK_BASEPATH_API):
			return Request.handler(self,method,path)
	
		""" Respond with JSON """
		self.json_response = True
	
		""" Route the request to the right handler """
		api_path = path.path[len(constants.NETWORK_BASEPATH_API):]
		api_route = self.get_route(method,api_path)
		if not api_route:
			raise Error("Not Found: %s" % path.path,constants.HTTP_STATUS_NOTFOUND)
		
		""" Get status as a JSON object """
		response = api_route.__get__(self,APIRequest)()
		if response==None:
			self.send_response(constants.HTTP_STATUS_NOCONTENT)
			self.end_headers()
		else:
			self.send_response(constants.HTTP_STATUS_OK)
			self.send_header('Content-type',"application/json")
			self.send_header('Date', self.date_time_string())
			self.end_headers()
			self.wfile.write(json.dumps(response))
			self.wfile.write("\n")

	def handler_status(self):
		return {
			"product": constants.PRODUCT_NAME,
			"version": constants.PRODUCT_VERSION,
			"timestamp": datetime.datetime.now().isoformat(),
			"name": self.server.server_name,
			"status": "idle"
		}

	def handler_shutdown(self):
		self.server.running = False

	ROUTES = (
		(Request.METHOD_GET,"v1/status",handler_status),
		(Request.METHOD_GET,"v1/shutdown",handler_shutdown),
	)


################################################################################

# Mime types lookup table
#class MimeTypes(object):
#	def __init__(self,file_path,default="application/octet-stream"):
#		assert isinstance(file_path,basestring)
#		self._default = default
#		self._lookup = { }
#		with open(file_path,'r') as data:
#			for line in data.readlines():
#				match = re.match("^([A-Za-z0-9\+\-\.\/\_]+)\s*([A-Za-z0-9\+\-\.\/\_\x20]+)$",line)
#				if not match:
#					continue
#				mimetype = match.group(1)
#				for extension in match.group(2).split():
#					self._lookup[extension] = mimetype
#	def get(self,extension):
#		return self._lookup.get(extension,self._default)

# HTTP Server Implementation
#class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
#	def __init__(self,bind,requestclass,webroot,mimetypes):
#		HTTPServer.__init__(self,bind,requestclass)
#		self.set_webroot(webroot)
#		self.set_mimetypes(mimetypes)
#	# properties
#	def get_webroot(self):
#		return self._webroot
#	def set_webroot(self,value):
#		assert isinstance(value,basestring)
#		assert os.path.isdir(value)
#		self._webroot = value
#	def get_mimetypes(self):
#		return self._mimetypes
#	def set_mimetypes(self,value):
#		assert isinstance(value,basestring)
#		assert os.path.isfile(value)
#		self._mimetypes = MimeTypes(value)
#
#	webroot = property(get_webroot,set_webroot)
#	mimetypes = property(get_mimetypes,set_mimetypes)
#
#	# public methods
#	def resolve_static_path(self,path):
#		""" Return absolute file path from URI path """
#		assert isinstance(path,basestring)
#		assert path.startswith('/')
#		relative_path = path[1:]
#		# fudge / and /favicon.ico
#		if relative_path=='':
#			relative_path = "index.html"
#		elif relative_path=='favicon.ico':
#			relative_path = "img/favicon.ico"
#		# get normalized absolute path
#		absolute_path = os.path.normpath(os.path.join(self.webroot,relative_path))
#		# ensure path is under the document root
#		if not absolute_path.startswith(self.webroot):
#			return None
#		# ensure path is a file
#		if not os.path.isfile(absolute_path):
#			return None
#		# return absolute path
#		return absolute_path
#	def content_type(self,path):
#		""" Return mimetype from file path """
#		file_extension = os.path.splitext(path)[1]
#		if file_extension.startswith('.'):
#			return self.mimetypes.get(file_extension[1:])
#		else:
#			return self.mimetypes.get(file_extension)
#
#
