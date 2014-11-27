#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python imports
import os,psutil

def system_info():
	p = psutil.Process(os.getpid())
	return {
		"cpu": p.get_cpu_percent()
	}
