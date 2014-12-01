
var STATUS_INTERVAL = 5 * 1000; // 5 secs

function AJAXResponse(request) {
	this.status = request.status;
	this.statusText = request.statusText;
	this.body = request.responseText;
	this._content_type = request.getResponseHeader('content-type') || "";
	
	this.mimetype = function() {
		var mimetype = this._content_type.match(/^\s*(.*[A-Z0-9]+)\/([A-Z0-9\-]+)[\;\s]?/i);
		if(mimetype && mimetype.length >= 3) {
			return mimetype[1] + "/" + mimetype[2];
		}
		return null;
	}
	
	this.is_json = function () {
		var mimetype = this._content_type.match(/^\s*(.*[A-Z0-9]+)\/([A-Z0-9\-]+)[\;\s]?/i);
		if(mimetype && mimetype.length >= 3) {
			var major = mimetype[1];
			var minor = mimetype[2];
			if(!major.match(/^(application|text)$/i)) {
				return false;
			}
			if(minor.match(/^json$/i)) {
				return true;
			}
			if(!minor.match(/^(x-)?(emca|java)script$/i)) {
				return false;
			}
			return true;
		} else {
			return false;
		}
	}
	
	this.json = function () {
		if(this.is_json()) {
			return JSON.parse(this.body);
		} else {
			return null;
		}
	}
}

function AJAX() {
	this.init = function (method,url,data,callback_success,callback_error) {
		this._callback_success = callback_success;
		this._callback_error = callback_error;
		var request =  new XMLHttpRequest();
		request.onreadystatechange = this.on_request_statechange.bind(this);
		request.open(method,url,true);
		request.send(data);
		console.log("AJAX: " + method + " " + url);
	}
	this.on_request_statechange = function(event) {
		var request = event.currentTarget;
		if(request.readyState < 4) { // not done
			return;
		}
		var response = this.response(request);
		if(response.status && response.status >= 200 && response.status <= 399) {
			// success
			if(this._callback_success) {
				this._callback_success(response);
			}
		} else {
			if(this._callback_error) {
				this._callback_error(response);
			} else {
				console.log("error: code " + response.status);
			}
		}
	}
	this.response = function(request) {
		return new AJAXResponse(request);
	}
}

function Livebox() {
	this.init = function () {
		this.doStatusTimer();
		this.doControlTimer();
		// start calling status
		window.setInterval(this.doStatusTimer.bind(this),STATUS_INTERVAL);
		return this;
	}
	this.doStatusTimer = function() {
		new AJAX().init("GET","/api/v1/status",null,this.doStatusResponse.bind(this),this.doErrorResponse.bind(this));
	}
	this.doControlTimer = function() {
		new AJAX().init("GET","/api/v1/control",null,this.doControlResponse.bind(this),this.doErrorResponse.bind(this));
	}
	this.doControlPost = function(evt) {
		var data = new FormData(evt.srcElement);
		new AJAX().init("POST","/api/v1/control",data,this.doControlResponse.bind(this),this.doErrorResponse.bind(this));
		this.doErrorClear();
		return false;
	}
	this.doStatusResponse = function(response) {
		// replace status element
		var node = document.getElementById('status-body');
		if(node) {
			node.innerText = response.body;
		}
	}
	this.doControlResponse = function(response) {
		// replace status element
		var node = document.getElementById('control-body');
		if(node) {
			node.innerText = response.body;
		}
		// set form values
		var form = document.getElementById('control-form');
		var json = response.json();
		if(form && json) {
			form.url.value = json.url;
			form.resolution.value = json.resolution;
			form.framerate.value = json.framerate;
			form.audio.value = json.audio;
			form.quality.value = json.quality ? json.quality : 0;
		}
	}
	this.doErrorResponse = function(response) {
		var node = document.getElementById('alert-box');
		var textnode = document.getElementById('alert-text');
		var buttonnode = document.getElementById('alert-button');
		if(node) {
			node.style.display = "block";
		}
		if(buttonnode) {
			buttonnode.onclick = this.doErrorClear.bind(this);
		}
		if(response.is_json()) {
			var json = response.json();
			textnode.innerText = "Error: " + json.reason;
		} else {
			textnode.innerText = "Error: " + response.statusText;
		}
	}
	this.doErrorClear = function() {
		var node = document.getElementById('alert-box');
		if(node) {
			node.style.display = "none";
		}
	}
	this.doStart = function () {
		new AJAX().init("GET","/api/v1/start",null,null,this.doErrorResponse.bind(this));
	}
	this.doStop = function () {
		new AJAX().init("GET","/api/v1/stop",null,null,this.doErrorResponse.bind(this));
	}
	this.doShutdown = function () {
		new AJAX().init("GET","/api/v1/shutdown",null,null,this.doErrorResponse.bind(this));
	}
}

window.onload = function() {
	var api = new Livebox().init();
	
	// link up the form
	var form = document.getElementById('control-form');
	if(form) {
		form.onsubmit = api.doControlPost.bind(api);
	}
	
	// link the buttons
	var start = document.getElementById('start-button');
	if(start) {
		start.onclick = api.doStart.bind(api);
	}
	var stop = document.getElementById('stop-button');
	if(stop) {
		stop.onclick = api.doStop.bind(api);
	}
	var shutdown = document.getElementById('shutdown-button');
	if(shutdown) {
		shutdown.onclick = api.doShutdown.bind(api);
	}
	
	
}

