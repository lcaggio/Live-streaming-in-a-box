#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python imports
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import urlparse,socket,os,logging,json
import datetime
import cgi

# local imports
import webserver
import camera,streamer,constants,util
from . import Control

################################################################################

class APIRequest(webserver.Request):

	def get_route(self,method,path):
		for route in APIRequest.ROUTES:
			assert isinstance(route,tuple) and len(route)==3
			if method != route[0]: continue
			if path != route[1]: continue
			return route[2]
		return None

	def handler(self,method,path):
		if not path.path.startswith(constants.NETWORK_BASEPATH_API):
			return webserver.Request.handler(self,method,path)
	
		""" Respond with JSON """
		self.json_response = True
	
		""" Route the request to the right handler """
		api_path = path.path[len(constants.NETWORK_BASEPATH_API):]
		api_route = self.get_route(method,api_path)
		if not api_route:
			raise webserver.Error("Not Found: %s" % path.path,webserver.HTTP_STATUS_NOTFOUND)
		
		""" Obtain the body """
		args = ()
		if method in (webserver.HTTP_METHOD_PUT,webserver.HTTP_METHOD_POST):
			body = self.get_content()
			args = (body, )
		
		""" Get status as a JSON object """
		response = api_route.__get__(self,APIRequest)(*args)
		if response==None:
			self.send_response(webserver.HTTP_STATUS_NOCONTENT)
			self.end_headers()
		else:
			self.send_response(webserver.HTTP_STATUS_OK)
			self.send_header('Content-type',"application/json")
			self.send_header('Date', self.date_time_string())
			self.end_headers()
			self.wfile.write(json.dumps(response))
			self.wfile.write("\n")

	def handler_get_control(self):
		return self.server.control.as_json()
	
	def handler_put_control(self,body):
		if not isinstance(body,dict):
			raise webserver.Error("Invalid control information",webserver.HTTP_STATUS_BADREQUEST)

		logging.debug("handler_put_control: %s" % body)

		# Test control values, then do it for real
		for control in (Control(),self.server.control):
			""" We reverse sort the keys so resolution gets set before bitrate """
			for key in sorted(body.keys(),reverse=True):
				value = body[key]
				if isinstance(value,list) and len(value)==1:
					""" If value is an array with one value in it """
					value = value[0]
				try:
					assert hasattr(control,key)
					setattr(control,key,value)
				except (AssertionError,ValueError):
					logging.debug("handler_put_control: exception raised setting value: '%s' => %s" % (key,value))
					raise webserver.Error("Invalid value for '%s'" % key,webserver.HTTP_STATUS_BADREQUEST)
		# Return the control structure
		return self.server.control.as_json()

	def handler_start_streamer(self):
		""" Start streaming from the camera """
		self.server.streamer_start()
		return self.handler_status()

	def handler_stop_streamer(self):
		""" Stop streaming from the camera """
		self.server.streamer_stop()
		return self.handler_status()

	def handler_status(self):
		return {
			"product": constants.PRODUCT_NAME,
			"version": constants.PRODUCT_VERSION,
			"timestamp": datetime.datetime.now().isoformat(),
			"name": self.server.server_name,
			"status": self.server.state,
			"system": util.system_info()
		}

	def handler_shutdown(self):
		self.server.running = False
		return self.handler_status()

	ROUTES = (
		(webserver.HTTP_METHOD_GET,"v1/status",handler_status),
		(webserver.HTTP_METHOD_GET,"v1/shutdown",handler_shutdown),
		(webserver.HTTP_METHOD_GET,"v1/control",handler_get_control),
		(webserver.HTTP_METHOD_PUT,"v1/control",handler_put_control),
		(webserver.HTTP_METHOD_POST,"v1/control",handler_put_control),
		(webserver.HTTP_METHOD_GET,"v1/start",handler_start_streamer),
		(webserver.HTTP_METHOD_GET,"v1/stop",handler_stop_streamer),
	)

################################################################################

class APIServer(webserver.Server):
	def __init__(self,ffmpeg,*args):
		webserver.Server.__init__(self,*args,request_class=APIRequest)
		self.control = Control()
		self.fifo = util.FIFO()
		self.camera = camera.Camera()
		self.streamer = streamer.Streamer(ffmpeg)

	""" Properties """
	def get_state(self):
		if not self.camera.running and not self.streamer.running:
			return "idle"
		else:
			return "running"
	state = property(get_state)
	
	""" Public methods """
	def run(self):
		logging.debug("run(): starting runloop, fifo=%s" % self.fifo.filename)
		webserver.Server.run(self)
		self.fifo.close()
		logging.debug("run(): stopped runloop")

	def streamer_start(self):
		try:
			self.streamer.start(self.fifo.filename,self.control)
			self.camera.start(self.fifo.filename,self.control)
		except (camera.Error,streamer.Error), e:
			raise webserver.Error("streamer_start: %s" % e,webserver.HTTP_STATUS_SERVERERROR)

	def streamer_stop(self):
		try:
			self.streamer.stop()
			self.camera.stop()
		except (camera.Error,streamer.Error), e:
			raise webserver.Error("streamer_stop: %s" % e,webserver.HTTP_STATUS_SERVERERROR)



