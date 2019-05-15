# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

def vshare(self, data):
	stream_url = re.search('source src="(.*?)" type="video/mp4"', data, re.S)
	if stream_url:
		stream_url.group(1)
		self._callback(stream_url.group(1))
	else:
		self.stream_not_found()