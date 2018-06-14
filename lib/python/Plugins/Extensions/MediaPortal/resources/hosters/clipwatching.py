	# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

def clipwatching(self, data):
	stream_url = re.findall('file:"(.*?)"', data)
	if stream_url:
		self._callback(stream_url[-1])
	else:
		self.stream_not_found()