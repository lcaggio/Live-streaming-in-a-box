#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python imports
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import urlparse,socket,os,logging,json,cgi

################################################################################

""" HTTP Status codes """
HTTP_STATUS_OK = 200
HTTP_STATUS_NOCONTENT = 204
HTTP_STATUS_BADREQUEST = 400
HTTP_STATUS_AUTHREQUIRED = 401
HTTP_STATUS_NOTFOUND = 404
HTTP_STATUS_SERVERERROR = 500

HTTP_INDEX_FILENAME = "index.html"

""" Mimetypes """
HTTP_MIMETYPES = (
	("","application/octet-stream"), # Default
	(".html","text/html"),
	(".txt","text/plain"),
	(".css","text/css"),
	(".js","application/javascript"),
	(".json","application/json"),
	(".png","image/png"),
	(".jpg","image/jpeg"),
	(".gif","image/gif"),
	(".ico","image/x-icon"),
)

""" Methods """
HTTP_METHOD_GET = 1
HTTP_METHOD_PUT = 2
HTTP_METHOD_POST = 3
HTTP_METHOD_DELETE = 4

################################################################################

class Error(Exception):
	def __init__(self,reason,code=HTTP_STATUS_SERVERERROR):
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

class Request(BaseHTTPRequestHandler):
	
	def handler(self,method,path):
		self.json_response = False # Normal error response
		
		""" Only allow GET requests """
		if method != HTTP_METHOD_GET:
			raise Error("Bad request: %s" % path.path,HTTP_STATUS_BADREQUEST)
		""" Handle static files """
		absolute_path = os.path.normpath(os.path.join(self.server.wwwroot,path.path.strip('/')))
		if not absolute_path.startswith(self.server.wwwroot):
			raise Error("Bad request: %s" % path.path,HTTP_STATUS_BADREQUEST)
		if not os.path.exists(absolute_path):
			raise Error("Not Found: %s" % path.path,HTTP_STATUS_NOTFOUND)

		""" Deal with index files """
		if os.path.isfile(absolute_path):
			pass
		elif os.path.isdir(absolute_path):
			absolute_path = os.path.join(absolute_path,HTTP_INDEX_FILENAME)

		""" Don't allow hidden files, get mimetype """
		(_,filename) = os.path.split(absolute_path)
		if filename.startswith("."):
			raise Error("Bad request: %s" % path.path,HTTP_STATUS_BADREQUEST)
		mimetype = self.server.get_mimetype(filename)

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

	def get_content(self):
		""" Get body content """
		try:
			ctype, pdict = cgi.parse_header(self.headers.getheader('Content-Type'))
			if ctype == 'multipart/form-data':
				postvars = cgi.parse_multipart(self.rfile, pdict)
			elif ctype == 'application/x-www-form-urlencoded':
				length = int(self.headers.getheader('content-length'))
				postvars = cgi.parse_qs(self.rfile.read(length),keep_blank_values=1)
			elif ctype == 'application/json':
				length = int(self.headers.getheader('content-length'))
				postvars = json.loads(self.rfile.read(length))
			else:
				raise ValueError()
		except (TypeError,ValueError):
			raise Error("Bad Request: %s" % self.path,HTTP_STATUS_BADREQUEST)
		return postvars

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
			return self.handler(HTTP_METHOD_POST,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)
	def do_PUT(self):
		try:
			return self.handler(HTTP_METHOD_PUT,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)
	def do_DELETE(self):
		try:
			return self.handler(HTTP_METHOD_DELETE,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)
	def do_GET(self):
		try:
			return self.handler(HTTP_METHOD_GET,urlparse.urlparse(self.path))
		except Error,e:
			self.send_error(e.code,e.reason)

################################################################################

class Server(HTTPServer):
	def __init__(self,bind,port,wwwroot,request_class=Request):
		assert isinstance(bind,basestring)
		assert isinstance(port,(int,long)) and port > 0
		assert isinstance(wwwroot,basestring) and os.path.isdir(wwwroot)

		try:
			HTTPServer.__init__(self,(bind,port),request_class)
		except socket.error, e:
			raise Error("Server bind error: %s" % e)

		self.running = False
		self.wwwroot = wwwroot
		self.mimetypes = dict(HTTP_MIMETYPES)
	
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

