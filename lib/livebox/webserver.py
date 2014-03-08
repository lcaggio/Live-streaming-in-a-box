
# python imports
import re, os, json
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn, ForkingMixIn

# Mime types lookup table
class MimeTypes(object):
	def __init__(self,file_path,default="application/octet-stream"):
		assert isinstance(file_path,basestring)
		self._default = default
		self._lookup = { }
		with open(file_path,'r') as data:
			for line in data.readlines():
				match = re.match("^([A-Za-z0-9\+\-\.\/\_]+)\s*([A-Za-z0-9\+\-\.\/\_\x20]+)$",line)
				if not match:
					continue
				mimetype = match.group(1)
				for extension in match.group(2).split():
					self._lookup[extension] = mimetype
	def get(self,extension):
		return self._lookup.get(extension,self._default)

class HTTPException(Exception):
	""" HTTP specific error response """
	STATUS_OK = 200
	STATUS_BADREQUEST = 400
	STATUS_NOTFOUND = 404
	STATUS_AUTHREQUIRED = 401
	STATUS_SERVERERROR = 500
	REASONS = {
		STATUS_OK: "OK",
		STATUS_BADREQUEST: "Bad Request",
		STATUS_NOTFOUND: "Resource not found",
		STATUS_SERVERERROR: "Server Error",
		STATUS_AUTHREQUIRED: "Authentication Required"
	}
	def __init__(self,code,reason=None,**kwargs):
		self._code = code
		self._reason = reason
		self._args = kwargs

	# PROPERTIES
	def get_code(self):
		return self._code
	def get_reason(self):
		if self._reason:
			return self._reason
		if self._code in HTTPException.REASONS:
			return HTTPException.REASONS[self._code]
		return "Error Code %s" % self.code
	def get_args(self):
		if isinstance(self._args,dict):
			return self._args
		return None
	code = property(get_code)
	reason = property(get_reason)
	args = property(get_args)
	# PUBLIC METHODS
	def as_json(self):
		json_dict = { '_type': type(self).__name__, 'code': self.code, 'reason': self.reason }
		for key in self.args:
			value = self.args[key]
			if isinstance(value,(bool,basestring,int,long)):
				json_dict[key] = value
		return json_dict

# HTTP Server Implementation
class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
	def __init__(self,bind,requestclass,webroot,mimetypes):
		HTTPServer.__init__(self,bind,requestclass)
		self.set_webroot(webroot)
		self.set_mimetypes(mimetypes)
	# properties
	def get_webroot(self):
		return self._webroot
	def set_webroot(self,value):
		assert isinstance(value,basestring)
		assert os.path.isdir(value)
		self._webroot = value
	def get_mimetypes(self):
		return self._mimetypes
	def set_mimetypes(self,value):
		assert isinstance(value,basestring)
		assert os.path.isfile(value)
		self._mimetypes = MimeTypes(value)

	webroot = property(get_webroot,set_webroot)
	mimetypes = property(get_mimetypes,set_mimetypes)

	# public methods
	def resolve_static_path(self,path):
		""" Return absolute file path from URI path """
		assert isinstance(path,basestring)
		assert path.startswith('/')
		relative_path = path[1:]
		# fudge / and /favicon.ico
		if relative_path=='':
			relative_path = "index.html"
		elif relative_path=='favicon.ico':
			relative_path = "img/favicon.ico"
		# get normalized absolute path
		absolute_path = os.path.normpath(os.path.join(self.webroot,relative_path))
		# ensure path is under the document root
		if not absolute_path.startswith(self.webroot):
			return None
		# ensure path is a file
		if not os.path.isfile(absolute_path):
			return None
		# return absolute path
		return absolute_path
	def content_type(self,path):
		""" Return mimetype from file path """
		file_extension = os.path.splitext(path)[1]
		if file_extension.startswith('.'):
			return self.mimetypes.get(file_extension[1:])
		else:
			return self.mimetypes.get(file_extension)


# HTTP Request implementation
class RequestHandler(BaseHTTPRequestHandler):
	METHOD_GET = 1
	METHOD_PUT = 2
	METHOD_POST = 3
	METHOD_DELETE = 4
	STATIC = 5
	# PRIVATE METHODS
	def _get_routes(self):
		"""Return tuple of routes"""
		if not 'routes' in vars(self.__class__):
			raise ValueError("Invalid 'routes' property for %s",self.__class__.__name__)
			return None
		assert isinstance(self.routes,tuple) or isinstance(self.routes,list),"_get_routes: Invalid routes class property"
		return self.routes
	def _decode_method(self):
		"""Decode the method into constants"""
		method = self.command
		if 'X-HTTP-Method-Override' in self.headers:
			# Hack for prototypejs and others which don't have PUT or DELETE methods
			method = self.headers['X-HTTP-Method-Override']
		if method=='GET':
			return RequestHandler.METHOD_GET
		if method=='POST':
			return RequestHandler.METHOD_POST
		if method=='DELETE':
			return RequestHandler.METHOD_DELETE
		if method=='PUT':
			return RequestHandler.METHOD_PUT
	def _response_json_impl(self,obj):
		if obj==None:
			return None
		elif isinstance(obj,(basestring,bool,int,long)):
			return obj
		elif isinstance(obj,(list,tuple)):
			json_value = [ ]
			for obj2 in obj:
				json_value.append(self._response_json_impl(obj2))
			return json_value
		elif isinstance(obj,dict):
			json_value = { }
			for (k,v) in obj.iteritems():
				json_value[k] = self._response_json_impl(v)
			return json_value
		else:
			raise ValueError("Invalid response object: %s" % type(obj).__name__)
	def _decode_request(self):
		"""Decode request body from JSON into a Python object"""
		try:
			if self.request.body:
				request = simplejson.loads(self.request.body)
				return request
			else:
				return None
		except (ValueError,KeyError), e:
			raise HTTPException(HTTPException.STATUS_BADREQUEST,"Bad request: %s" % e)
	def route_request(self):
		"""Call appropriate matched route for web request"""
		method = self._decode_method()
		path = self.path
		assert isinstance(method,int) or isinstance(method,long),"route_request: Unexpected method"
		assert isinstance(path,basestring),"route_request: Unexpected path"
		for route in self._get_routes():
			assert isinstance(route,tuple) or isinstance(route,list),"route_request: Invalid route"
			assert route[0]==RequestHandler.STATIC or len(route) >= 3,"route_request: Invalid route"
			# skip route if not correct method
			if route[0]==RequestHandler.STATIC:
				if method != RequestHandler.METHOD_GET: continue
			elif route[0] != method:
				continue
			# match route to path
			m = re.match(route[1],path)
			if not m:
				continue
			# if static, then return this
			if route[0]==RequestHandler.STATIC:
				return self.route_static()
			# get route arguments
			args = list(m.groups())
			# where requests are POST or PUT, append the JSON body to the arguments
			if method in (RequestHandler.METHOD_POST,RequestHandler.METHOD_PUT):
				args.append(self._decode_request())
			# call routing method
			return route[2](self,*args)
		raise HTTPException(HTTPException.STATUS_NOTFOUND,reason="Not found, unknown path: %s" % path)
	def route_static(self):
		absolute_path = self.server.resolve_static_path(self.path)
		if absolute_path==None:
			return self.send_error(404,'Not Found: %s' % self.path)
		try:
			content_type = self.server.content_type(absolute_path)
			content_length = os.path.getsize(absolute_path)
			with open(absolute_path,'r') as data:
				self.send_response(200)
				self.send_header('Content-Type',content_type)
				self.send_header('Content-Length',content_length)
				self.end_headers()
				self.wfile.write(data.read())
		except IOError:
			self.send_error(404, 'Not Found: %s (%s)' % (self.path,absolute_path))
	def response_json(self,obj):
		"""Send response to client"""
		if isinstance(obj,HTTPException):
			self.send_response(obj.code)
			self.send_header('Content-Type',"application/json")
			self.end_headers()
			self.wfile.write(json.dumps(obj.as_json()))
		else:
			self.send_response(200)
			self.send_header('Content-Type',"application/json")
			self.end_headers()
			self.wfile.write(json.dumps(self._response_json_impl(obj)))
	def do_GET(self):
		try:
			return self.route_request()
		except HTTPException, e:
			return self.response_json(e)
	def do_DELETE(self):
		try:
			return self.route_request()
		except HTTPException, e:
			return self.response_json(e)
	def do_PUT(self):
		try:
			return self.route_request()
		except HTTPException, e:
			return self.response_json(e)
	def do_POST(self):
		try:
			return self.route_request()
		except HTTPException, e:
			return self.response_json(e)
