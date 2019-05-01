# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

def bitporno(self, data):
	stream_url = re.findall('source\ssrc="(.*?\.mp4)"\stype="video/mp4"', data, re.S)
	if stream_url:
		url = stream_url[-1]
		self._callback(url)
	else:
		self.stream_not_found()