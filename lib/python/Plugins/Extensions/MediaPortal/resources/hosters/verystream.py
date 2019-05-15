# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

def verystream(self, data, id, link):
	videolink = re.search('(%s~[~.:a-zA-Z0-9]+)' % id, data)
	if videolink:
		url = "https://verystream.com/gettoken/%s?mime=true" % videolink.group(1)
		tw_agent_hlp = TwAgentHelper()
		tw_agent_hlp.getRedirectedUrl(url).addCallback(self.verystreamUrl, id, link).addErrback(self.errorload)
	else:
		self.stream_not_found()

def verystreamUrl(self, url, id, link):
	if url.startswith('https://verystream.com/gettoken'):
		if self.retry <=3:
			self.retry += 1
			twAgentGetPage(link, agent=self.agent, headers={'referer':self.referer}).addCallback(self.verystream, id, link).addErrback(self.errorload)
		else:
			self.stream_not_found()
	else:
		self._callback(url)