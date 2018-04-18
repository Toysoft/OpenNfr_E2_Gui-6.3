# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

def fembed(self, data):
	json_data = json.loads(data)
	stream_url = re.findall('file":"(.*?)"', json_data["data"])
	if stream_url:
		self._callback(str(stream_url[-1]).replace('\/','/'))
	else:
		self.stream_not_found()