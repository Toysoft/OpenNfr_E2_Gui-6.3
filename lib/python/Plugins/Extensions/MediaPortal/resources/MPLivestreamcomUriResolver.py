# -*- coding: utf-8 -*-
#######################################################################################################
#
#    MediaPortal for Dreambox OS
#
#    Coded by MediaPortal Team (c) 2013-2019
#
#  This plugin is open source but it is NOT free software.
#
#  This plugin may only be distributed to and executed on hardware which
#  is licensed by Dream Property GmbH. This includes commercial distribution.
#  In other words:
#  It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
#  to hardware which is NOT licensed by Dream Property GmbH.
#  It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
#  on hardware which is NOT licensed by Dream Property GmbH.
#
#  This applies to the source code as a whole as well as to parts of it, unless explicitely
#  stated otherwise.
#
#  If you want to use or modify the code or parts of it, permission from the authors is necessary.
#  You have to keep OUR license and inform us about any modification, but it may NOT be distributed
#  other than under the conditions noted above.
#
#  As an exception regarding modifcations, you are NOT permitted to remove
#  any copy protections implemented in this plugin or change them for means of disabling
#  or working around the copy protections, unless the change has been explicitly permitted
#  by the original authors. Also decompiling and modification of the closed source
#  parts is NOT permitted.
#
#  Advertising with this plugin is NOT allowed.
#
#  For other uses, permission from the authors is necessary.
#
#######################################################################################################

try:
	from enigma import eServiceReference, eUriResolver, StringList
	from twagenthelper import twAgentGetPage
	from imports import *
	import re

	from Tools.Log import Log

	class MPLivestreamcomUriResolver(eUriResolver):

		_schemas = ("mp_livestreamcom",)
		instance = None

		def __init__(self):
			eUriResolver.__init__(self, StringList(self._schemas))
			Log.i(self._schemas)

		def resolve(self, service, uri):
			Log.i(uri)
			uri = uri.replace('mp_livestreamcom://','').lower().strip()
			def onUrlReady(uri):
				try:
					if not service.ptrValid():
						Log.w("Service became invalid!")
						return
					if uri:
						service.setResolvedUri(uri, eServiceReference.idGST)
					else:
						service.failedToResolveUri()
				except:
					service.failedToResolveUri()

			if uri:
				twAgentGetPage(uri).addCallback(self.parseLive, service)
			else:
				service.failedToResolveUri()

			return True

		def parseLive(self, data, service):
			data = data.replace('\/','/')
			urls = re.findall('m3u8_url":"(.*?)"', data, re.S)
			if urls:
				uri = urls[-1]
			try:
				if not service.ptrValid():
					Log.w("Service became invalid!")
					return
				if uri:
					twAgentGetPage(uri).addCallback(self.parseData, service)
				else:
					service.failedToResolveUri()
			except:
				service.failedToResolveUri()

		def parseData(self, data, service):
			self.bandwith_list = []
			match_sec_m3u8=re.findall('BANDWIDTH=(\d+).*?\n(.*?m3u8.*?)\n', data, re.S)
			max = 0
			for x in match_sec_m3u8:
				if int(x[0]) > max:
					max = int(x[0])
			videoPrio = int(config_mp.mediaportal.videoquali_others.value)
			if videoPrio == 2:
				bw = max
			elif videoPrio == 1:
				bw = max/2
			else:
				bw = max/3
			for each in match_sec_m3u8:
				bandwith,url = each
				self.bandwith_list.append((int(bandwith),url))
			_, best = min((abs(int(x[0]) - bw), x) for x in self.bandwith_list)
			uri = best[1]
			try:
				if not service.ptrValid():
					Log.w("Service became invalid!")
					return
				if uri:
					service.setResolvedUri(uri, eServiceReference.idDVB)
				else:
					service.failedToResolveUri()
			except:
				service.failedToResolveUri()
except ImportError:
	pass