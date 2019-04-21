# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
import subprocess

def vidup(self, data):
	thief = re.search("var thief='(.*?)';", data, re.S)
	stream_url = re.findall('"file":"(.*?)",', data, re.S)

	if thief and stream_url:
		url = "https://vidup.tv/jwv/" + thief.group(1)
		twAgentGetPage(url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36').addCallback(self.vidup_thief, stream_url[-1]).addErrback(self.errorload)
	else:
		self.stream_not_found()

def vidup_thief(self, data, stream_url):
	decoder = data.replace('eval','var foo = ')
	js = decoder + ";\nconsole.log(foo);"
	try:
		sUnpacked = subprocess.check_output(["node", "-e", js]).strip()
	except OSError as e:
		if e.errno == 2:
			self.session.open(MessageBoxExt, _("This plugin requires package nodejs."), MessageBoxExt.TYPE_INFO)
	except Exception:
		self.session.open(MessageBoxExt, _("Error executing Javascript, please report to the developers."), MessageBoxExt.TYPE_INFO)
	if sUnpacked:
		b = re.search('b="(.*?)",', sUnpacked)
		c = re.search('c="(.*?)";', sUnpacked)
		if b and c:
			vidurl = stream_url + "?direct=false" + "&" + b.group(1) + "&" + c.group(1)
			self._callback(vidurl)
		else:
			self.stream_not_found()
	else:
		self.stream_not_found()