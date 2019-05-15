# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.messageboxext import MessageBoxExt

def streamcloud(self, data):
	id = re.findall('<input type="hidden" name="id".*?value="(.*?)">', data)
	fname = re.findall('<input type="hidden" name="fname".*?alue="(.*?)">', data)
	if id and fname:
		url = "http://streamcloud.eu/%s" % id[0]
		post_data = urllib.urlencode({'op': 'download1', 'usr_login': '', 'id': id[0], 'fname': fname[0], 'referer': url, 'hash': '', 'imhuman':'Weiter zum Video'})
		reactor.callLater(10, self.streamcloud_getpage, url, post_data)
		message = self.session.open(MessageBoxExt, _("Stream starts in 10 sec."), MessageBoxExt.TYPE_INFO, timeout=10)
	else:
		self.stream_not_found()

def streamcloud_getpage(self, url, post_data):
	spezialagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
	getPage(url, method='POST', cookies=self.ck, agent=spezialagent, postdata=post_data, headers={'Content-Type':'application/x-www-form-urlencoded', 'Referer': url, 'Origin':'http://streamcloud.eu'}).addCallback(self.streamcloud_data, url).addErrback(self.errorload)

def streamcloud_data(self, data, url):
	stream_url = re.findall('file:\s"(.*?)",', data)
	if stream_url:
		mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
		headers = '&Referer=' + url
		stream = stream_url[0] + '#User-Agent='+mp_globals.player_agent+headers
		self._callback(stream)
	elif re.search('This video is encoding now', data, re.S):
		self.session.open(MessageBoxExt, _("This video is encoding now. Please check back later."), MessageBoxExt.TYPE_INFO, timeout=10)
	else:
		self.stream_not_found()