
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
	this.init = function (method,url,callback_success,callback_error) {
		this._callback_success = callback_success;
		this._callback_error = callback_error;
		var request =  new XMLHttpRequest();
		request.onreadystatechange = this.on_request_statechange.bind(this);
		request.open(method,url,true);
		request.send();
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
	}
	this.doStatusTimer = function() {
		new AJAX().init("GET","/api/v1/status",this.doStatusResponse.bind(this));
	}
	this.doControlTimer = function() {
		new AJAX().init("GET","/api/v1/control",this.doControlResponse.bind(this));
	}
	this.doStatusResponse = function(response) {
		// replace status element
		var statusNode = document.getElementById('status-body');
		if(statusNode) {
			statusNode.innerText = response.body;
		}
	}
	this.doControlResponse = function(response) {
		// replace status element
		var node = document.getElementById('control-body');
		if(node) {
			node.innerText = response.body;
		}
	}
}

window.onload = function() {
	var api = new Livebox().init();
}

