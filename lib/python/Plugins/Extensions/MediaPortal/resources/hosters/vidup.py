# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.messageboxext import MessageBoxExt

def vidup(self, data, host, id):
	stream_url = re.findall('"\d+p":"(.*?)"', data, re.S)
	if stream_url:
		self._callback(stream_url[-1])
	else:
		if "captcha" in data:
			link = host + '/api/pair/' + id
			twAgentGetPage(link, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36').addCallback(self.vidup_pair, host).addErrback(self.errorload)
		else:
			self.stream_not_found()

def vidup_pair(self, data, host):
	stream_url = re.findall('"\d+p":"(.*?)"', data, re.S)
	if stream_url:
		self._callback(stream_url[-1])
	else:
		if "IP is not currently paired" in data:
			message = self.session.open(MessageBoxExt, _("IP address not authorized. Visit %s/pair to pair your IP.") % host, MessageBoxExt.TYPE_ERROR)
		else:
			self.stream_not_found()