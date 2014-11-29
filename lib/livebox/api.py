#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python imports
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import urlparse,socket,os,logging,json
import datetime
import cgi

# local imports
from webserver import Request
from . import constants,util
from . import Control

################################################################################

class APIServer(webserver.Server):
	pass


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
			return Request.handler(self,method,path)
	
		""" Respond with JSON """
		self.json_response = True
	
		""" Route the request to the right handler """
		api_path = path.path[len(constants.NETWORK_BASEPATH_API):]
		api_route = self.get_route(method,api_path)
		if not api_route:
			raise Error("Not Found: %s" % path.path,webserver.HTTP_STATUS_NOTFOUND)
		
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
			raise Error("Invalid control information",webserver.HTTP_STATUS_BADREQUEST)

		# Test properties
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
					raise Error("Invalid value for '%s'" % key,webserver.HTTP_STATUS_BADREQUEST)
		# Return the control structure
		return self.server.control.as_json()

	def handler_start_streamer(self,body):
		""" Start streaming from the camera """
		self.server.streamer_start()

	def handler_stop_streamer(self,body):
		""" Stop streaming from the camera """
		self.server.streamer_stop()

	def handler_status(self):
		return {
			"product": constants.PRODUCT_NAME,
			"version": constants.PRODUCT_VERSION,
			"timestamp": datetime.datetime.now().isoformat(),
			"name": self.server.server_name,
			"status": "idle",
			"system": util.system_info()
		}

	def handler_shutdown(self):
		self.server.running = False

	ROUTES = (
		(Request.METHOD_GET,"v1/status",handler_status),
		(Request.METHOD_GET,"v1/shutdown",handler_shutdown),
		(Request.METHOD_GET,"v1/control",handler_get_control),
		(Request.METHOD_PUT,"v1/control",handler_put_control),
		(Request.METHOD_POST,"v1/control",handler_put_control),
		(Request.METHOD_PUT,"v1/start",handler_start_streamer),
		(Request.METHOD_PUT,"v1/stop",handler_stop_streamer),
	)

