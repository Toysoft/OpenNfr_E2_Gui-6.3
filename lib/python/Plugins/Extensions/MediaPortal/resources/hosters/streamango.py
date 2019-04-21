# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.messageboxext import MessageBoxExt
from Plugins.Extensions.MediaPortal.resources.packer import unpack, detect
import subprocess

def streamango(self, data):
	get_packedjava = re.findall("mango.js.*?(eval.function.*?\{\}\)\))", data, re.S)
	if get_packedjava and detect(get_packedjava[0]):
		sJavascript = get_packedjava[0]
		sUnpacked = unpack(sJavascript)
		if sUnpacked:
			url = None
			js = sUnpacked.decode('string_escape').replace('window.d=function','d=function')
			dec = re.findall('video\/mp4\",src:(.*?\)),', data, re.S)
			js = js + ';\nvidurl = ' + dec[0] + ';\nconsole.log(vidurl);'
			try:
				url = subprocess.check_output(["node", "-e", js]).strip()
			except OSError as e:
				if e.errno == 2:
					self.session.open(MessageBoxExt, _("This plugin requires package nodejs."), MessageBoxExt.TYPE_INFO)
			except Exception:
				self.session.open(MessageBoxExt, _("Error executing Javascript, please report to the developers."), MessageBoxExt.TYPE_INFO)
			if url:
				if url.startswith('//'):
					url = 'https:' + url
				self._callback(url)
			else:
				self.stream_not_found()
		else:
			self.stream_not_found()
	else:
		self.stream_not_found()