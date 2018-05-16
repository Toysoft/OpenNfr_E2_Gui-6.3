# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

def filebebo(self, data):
	stream_url = re.search('source\ssrc="(.*?)"', data)
	if stream_url:
		self._callback(stream_url.group(1))
	else:
		self.stream_not_found()