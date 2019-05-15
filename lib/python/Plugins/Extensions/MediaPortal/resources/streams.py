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

from Plugins.Extensions.MediaPortal.plugin import _
from imports import *
import mp_globals
from debuglog import printlog as printl
from messageboxext import MessageBoxExt
from realdebrid import realdebrid_oauth2

try:
	import requests
except:
	requestsModule = False
else:
	requestsModule = True

ck = {}

def isSupportedHoster(linkOrHoster):
	if not linkOrHoster:
		return False

	printl("check hoster: %s" % linkOrHoster,'',"S")

	host = linkOrHoster.lower().strip()
	match1 = re.search(mp_globals.hosters[0], host)
	if match1:
		names = [name for name, value in match1.groupdict().iteritems() if value is not None]
		ret = names[0].replace('_space_',' ').replace('_dot_','.').replace('___','')
		if linkOrHoster.endswith('HD'):
			ret = ret + ' HD'
		printl("match1: %s" % ret,'',"H")
		return ret
	match2 = re.search(mp_globals.hosters[1], host)
	if match2:
		names = [name for name, value in match2.groupdict().iteritems() if value is not None]
		ret = names[0].replace('_space_',' ').replace('_dot_','.').replace('___','')
		if linkOrHoster.endswith('HD'):
			ret = ret + ' HD'
		printl("match2: %s" % ret,'',"H")
		return ret

	printl("hoster not supported",'',"H")
	return False

class get_stream_link:

	# hosters
	from hosters.bitporno import bitporno
	from hosters.bitshare import bitshare, bitshare_start
	from hosters.clipwatching import clipwatching
	from hosters.datoporn import datoporn
	from hosters.fembed import fembed
	from hosters.flashx import flashx
	from hosters.flyflv import flyflv, flyflvData
	from hosters.google import google
	from hosters.gounlimited import gounlimited
	from hosters.kissmovies import kissmovies
	from hosters.mailru import mailru
	from hosters.mp4upload import mp4upload
	from hosters.okru import okru
	from hosters.openload import openload
	from hosters.rapidvideocom import rapidvideocom
	from hosters.smartshare import smartshare
	from hosters.streamcloud import streamcloud, streamcloud_getpage, streamcloud_data
	from hosters.streamango import streamango
	from hosters.uptostream import uptostream
	from hosters.vcdn import vcdn
	from hosters.verystream import verystream, verystreamUrl
	from hosters.vidcloud import vidcloud
	from hosters.videowood import videowood
	from hosters.vidfast import vidfast
	from hosters.vidlox import vidlox
	from hosters.vidoza import vidoza
	from hosters.vidspot import vidspot
	from hosters.vidto import vidto
	from hosters.vidup import vidup
	from hosters.vidzi import vidzi
	from hosters.vivo import vivo
	from hosters.vkme import vkme, vkmeHash, vkmeHashGet, vkmeHashData, vkPrivat, vkPrivatData
	from hosters.vshare import vshare
	from hosters.yourupload import yourupload
	from hosters.youwatch import youwatch, youwatchLink

	def __init__(self, session):
		self._callback = None
		self.session = session
		self.papikey = config_mp.mediaportal.premiumize_password.value
		self.papiurl = "https://www.premiumize.me/api/transfer/directdl?apikey=%s" % self.papikey
		self.rdb = 0
		self.prz = 0
		self.fallback = False

	def callPremium(self, link):
		if self.rdb == 1 and config_mp.mediaportal.realdebrid_use.value:
			self.session.openWithCallback(self.rapiCallback, realdebrid_oauth2, str(link))
		elif self.prz == 1 and config_mp.mediaportal.premiumize_use.value:
			postdata = {'src':link}
			twAgentGetPage(self.papiurl, method='POST', postdata=urlencode(postdata), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.papiCallback, link).addErrback(self.errorload)

	def callPremiumYT(self, link, val):
		if val == "prz":
			postdata = {'src':link}
			twAgentGetPage(self.papiurl, method='POST', postdata=urlencode(postdata), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.papiCallback, link).addErrback(self.errorload)
		if val == "rdb":
			self.session.openWithCallback(self.rapiCallback, realdebrid_oauth2, str(link))

	def rapiCallback(self, stream_url, link):
		if stream_url:
				mp_globals.realdebrid = True
				mp_globals.premiumize = False
				self._callback(stream_url)
		elif self.prz == 1 and config_mp.mediaportal.premiumize_use.value:
			self.rdb = 0
			postdata = {'src':link}
			twAgentGetPage(self.papiurl, method='POST', postdata=urlencode(postdata), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.papiCallback, link).addErrback(self.errorload)
		else:
			self.fallback = True
			self.check_link(self.link, self._callback)

	def papiCallback(self, data, link):
		json_data = json.loads(data)
		if json_data["status"] == "success":
			stream_url = str(json_data["location"])
			if stream_url:
				if "&sig=" in stream_url:
					url = stream_url.split('&sig=')
					sig = ''
					filename = ''
					if "&f=" in stream_url:
						file = url[1].split('&f=')
						sig = "&sig=" + file[0].replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B')
						filename = "&f=" + file[1]
					else:
						sig = "&sig=" + url[1].replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B')
					url = url[0] + sig + filename
				else:
					url = stream_url
				mp_globals.premiumize = True
				mp_globals.realdebrid = False
				self._callback(url)
			else:
				self.fallback = True
				self.check_link(self.link, self._callback)
		elif self.rdb == 1 and config_mp.mediaportal.realdebrid_use.value:
			self.prz = 0
			self.session.openWithCallback(self.rapiCallback, realdebrid_oauth2, str(link))
		elif json_data["status"] == "error":
			self.session.openWithCallback(self.papiCallback2, MessageBoxExt, "premiumize: %s" % str(json_data["message"]), MessageBoxExt.TYPE_INFO, timeout=3)
		else:
			self.papiCallback2(True)

	def papiCallback2(self, answer):
		self.fallback = True
		self.check_link(self.link, self._callback)

	def check_link(self, data, got_link):
		self._callback = got_link
		self.link = data
		if data:
			if re.search("http://streamcloud.eu/", data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					link = re.search("(http://streamcloud.eu/\w+)", data, re.S)
					if link:
						link = link.group(1)
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					spezialagent = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0'
					self.ck = {}
					getPage(link, cookies=self.ck, agent=spezialagent).addCallback(self.streamcloud).addErrback(self.errorload)

			elif re.search('rapidgator.net|rg.to', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('turbobit.net', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('4shared.com', data, re.S):
				link = data
				if config_mp.mediaportal.realdebrid_use.value and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('vimeo.com', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('filerio.com|filerio.in', data, re.S):
				link = data
				if config_mp.mediaportal.realdebrid_use.value and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('filer.net', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('extmatrix.com', data, re.S):
				link = data
				if config_mp.mediaportal.realdebrid_use.value and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('mediafire.com', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('filefactory.com', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('gigapeta.com', data, re.S):
				link = data
				if config_mp.mediaportal.realdebrid_use.value and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('salefiles.com', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('oboom.com', data, re.S):
				link = data
				if config_mp.mediaportal.realdebrid_use.value and not self.fallback:
					self.rdb = 1
					self.prz = 0
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('uploaded.net|uploaded.to|ul.to', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('youtube.com', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					if config_mp.mediaportal.sp_use_yt_with_proxy.value == "rdb":
						self.callPremiumYT(link, "rdb")
					if config_mp.mediaportal.sp_use_yt_with_proxy.value == "prz":
						self.callPremiumYT(link, "prz")
				else:
					self.only_premium()

			elif re.search('bangbrothers.net', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('brazzers.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('ddfnetwork.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('teamskeet.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('naughtyamerica.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('wicked.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('digitalplayground.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('mofos.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('nubilefilms.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('julesjordan.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('kink.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('badoinkvr.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('realitykings.com', data, re.S):
				link = data
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('1fichier.com', data, re.S):
				link = data
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					self.only_premium()

			elif re.search('http://.*?bitshare.com', data, re.S):
				link = data
				getPage(link).addCallback(self.bitshare).addErrback(self.errorload)

			elif re.search('clipwatching.com', data, re.S):
				link = data
				twAgentGetPage(link).addCallback(self.clipwatching).addErrback(self.errorload)

			elif re.search('vidup\.(?:tv|io)|vev\.(?:io)', data, re.S):
				link = data.replace('/embed','').rsplit('/', 1)
				link = link[0] + '/api/serve/video/' + link[1]
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
				twAgentGetPage(link, method='POST', agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36', headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.vidup).addErrback(self.errorload)

			elif re.search('bitporno.com', data, re.S):
				if "/e/" in data:
					data = data.replace('/e/','/v/')
				if "&" in data:
					data = data.split('&')[0]
				link = data
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
				twAgentGetPage(link, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36', timeout=60).addCallback(self.bitporno).addErrback(self.errorload)

			elif re.search('fembed.com', data, re.S):
				link = 'http://www.fembed.com/api/source/' + data.split('/v/')[-1]
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
				twAgentGetPage(link, method='POST', agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36', headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.fembed).addErrback(self.errorload)

			elif re.search('smartshare.tv', data, re.S):
				link = 'https://smartshare.tv/api/source/' + data.split('/v/')[-1]
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
				twAgentGetPage(link, method='POST', agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36', headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.smartshare).addErrback(self.errorload)

			elif re.search('kissmovies.cc', data, re.S):
				link = 'https://kissmovies.cc/api/source/' + data.split('/v/')[-1]
				print link
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
				twAgentGetPage(link, method='POST', agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36', headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.kissmovies).addErrback(self.errorload)

			elif re.search('vcdn.io', data, re.S):
				link = 'https://vcdn.io/api/source/' + data.split('/v/')[-1]
				print link
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
				twAgentGetPage(link, method='POST', agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36', headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.vcdn).addErrback(self.errorload)

			elif re.search('flashx.tv|flashx.pw|flashx.co|flashx.to', data, re.S):
				link = data
				id = re.search('flashx.(tv|pw|co|to)/(embed-|dl\?|fxplay-|embed.php\?c=|)(\w+)', data)
				if id:
					link = "https://www.flashx.co/%s.html" % id.group(3)
					if config_mp.mediaportal.premiumize_use.value and not self.fallback:
						self.rdb = 1
						self.prz = 1
						TwAgentHelper().getRedirectedUrl(link).addCallback(self.flashx).addErrback(self.errorload)
					else:
						self.only_premium()
				else:
					self.stream_not_found()

			elif re.search('vk.com|vk.me', data, re.S):
				link = data
				getPage(link).addCallback(self.vkme, link).addErrback(self.errorload)

			elif re.search('http://youwatch.org', data, re.S):
				link = data
				id = link.split('org/')
				url = "http://youwatch.org/embed-%s.html" % id[1]
				getPage(url).addCallback(self.youwatch).addErrback(self.errorload)

			elif re.search("mp4upload.com", data, re.S):
				link = data
				getPage(link).addCallback(self.mp4upload).addErrback(self.errorload)

			elif re.search("dato.porn|datoporn.co", data, re.S):
				if "embed-" in data:
					link = data
				else:
					link = "https://datoporn.co/embed-" + data.split('/')[-1] + ".html"
				twAgentGetPage(link).addCallback(self.datoporn).addErrback(self.errorload)

			elif re.search("gounlimited.to", data, re.S):
				link = data
				twAgentGetPage(link).addCallback(self.gounlimited).addErrback(self.errorload)

			elif re.search("uptostream.com", data, re.S):
				link = data
				getPage(link).addCallback(self.uptostream).addErrback(self.errorload)

			elif re.search("yourupload.com|vidwoot.com", data, re.S):
				link = data
				getPage(link).addCallback(self.yourupload).addErrback(self.errorload)

			elif re.search("flyflv\.com", data, re.S):
				link = data
				getPage(link).addCallback(self.flyflv).addErrback(self.errorload)

			elif re.search("videowood\.tv", data, re.S):
				link = data
				if re.search('videowood\.tv/embed', data, re.S):
					link = data
				else:
					id = re.search('videowood\.tv/.*?/(\w+)', data)
					if id:
						link = "http://videowood.tv/embed/%s" % id.group(1)
				getPage(link).addCallback(self.videowood).addErrback(self.errorload)

			elif re.search("vivo.sx", data, re.S):
				link = data.replace('http:','https:')
				twAgentGetPage(link).addCallback(self.vivo, link).addErrback(self.errorload)

			elif re.search('vidto\.me/', data, re.S):
				if re.search('vidto\.me/embed-', data, re.S):
					link = data
				else:
					id = re.search('vidto\.me/(\w+)', data)
					if id:
						link = "http://vidto.me/embed-%s-640x360.html" % id.group(1)
				if config_mp.mediaportal.premiumize_use.value and not self.fallback:
					self.rdb = 0
					self.prz = 1
					self.callPremium(link)
				else:
					ck.update({'referer':'%s' % link })
					getPage(link, cookies=ck).addCallback(self.vidto).addErrback(self.errorload)


			elif re.search('vshare\.eu/', data, re.S):
				if not "embed-" in data:
					link = data.replace('.htm','').rsplit('/', 1)
					link = "https://vshare.eu/embed-%s.html" % link[-1]
				else:
					link = data
				twAgentGetPage(link).addCallback(self.vshare).addErrback(self.errorload)

			elif re.search('vidoza\.net/', data, re.S):
				link = data.replace('https','http')
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					twAgentGetPage(link).addCallback(self.vidoza).addErrback(self.errorload)

			elif re.search('vidspot\.net/', data, re.S):
				if re.search('vidspot\.net/embed', data, re.S):
					link = data
				else:
					id = re.findall('vidspot\.net/(.*?)$', data)
					if id:
						link = "http://vidspot.net/embed-%s.html" % id[0]
				getPage(link).addCallback(self.vidspot).addErrback(self.errorload)

			elif re.search('(docs|drive)\.google\.com/|youtube\.googleapis\.com|googleusercontent.com', data, re.S):
				if 'youtube.googleapis.com' in data:
					docid = re.search('docid=([\w]+)', data)
					link = 'https://drive.google.com/file/d/%s/edit' % docid.groups(1)
				else:
					link = data
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
				self.google_ck = {}
				if "googleusercontent.com" in link:
					import requests
					s = requests.session()
					try:
						page = s.head(link, allow_redirects=False, timeout=15)
						link = page.headers['Location']
						self.google_ck = requests.utils.dict_from_cookiejar(s.cookies)
						headers = '&Cookie=%s' % ','.join(['%s=%s' % (key, urllib.quote_plus(self.google_ck[key])) for key in self.google_ck])
						url = link.replace("\u003d","=").replace("\u0026","&") + '#User-Agent='+mp_globals.player_agent+headers
						self._callback(url)
					except:
						pass
				else:
					getPage(link, agent=mp_globals.player_agent, cookies=self.google_ck).addCallback(self.google).addErrback(self.errorload)

			elif re.search('rapidvideo\.com', data, re.S):
				link = data.replace('rapidvideo.com/e/', 'rapidvideo.com/v/')
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					id = re.findall('rapidvideo\.com/v/(.*?)$', link)
					if id:
						link = "http://rapidvideo.com/embed/%s" % id[0]
					getPage(link).addCallback(self.rapidvideocom).addErrback(self.errorload)

			elif re.search('openload\.(?:co|io|link|pw)|oload\.(?:tv|stream|site|xyz|win|download|cloud|cc|icu|fun|club|info|pw|live|space|services)|oladblock\.(?:services|xyz|me)|openloed\.co', data, re.S):
				link = data
				id = re.search('http[s]?://(?:openload\.(?:co|io|link|pw)|oload\.(?:tv|stream|site|xyz|win|download|cloud|cc|icu|fun|club|info|pw|live|space|services)|oladblock\.(?:services|xyz|me)|openloed\.co)\/[^/]+\/(.*?)(?:\/.*?)?$', link, re.S)
				if id:
					link = 'https://openload.co/embed/' + id.group(1)
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					url = "https://api.openload.co/1/streaming/get?file=" + id.group(1)
					getPage(url).addCallback(self.openload, link).addErrback(self.errorload)

			elif re.search('ok\.ru', data, re.S):
				id = data.split('/')[-1]
				url = "http://www.ok.ru/dk"
				mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
				dataPost = {'cmd': 'videoPlayerMetadata', 'mid': str(id)}
				getPage(url, method='POST', agent=mp_globals.player_agent, cookies=ck, postdata=urlencode(dataPost), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.okru).addErrback(self.errorload)

			elif re.search('mail\.ru', data, re.S):
				id_raw = re.findall('mail.ru/video/embed/(\d+)$', data)
				if id_raw:
					url = "https://my.mail.ru/+/video/meta/%s" % id_raw[0]
					spezialagent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
					mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
					kekse = {}
					getPage(url, agent=spezialagent, cookies=kekse).addCallback(self.mailru, kekse).addErrback(self.errorload)
				else:
					self.stream_not_found()

			elif re.search('vidzi\.tv/', data, re.S):
				link = data
				getPage(link, cookies=ck).addCallback(self.vidzi).addErrback(self.errorload)

			elif re.search('vidfast\.co/', data, re.S):
				link = data
				agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
				mp_globals.player_agent = agent
				twAgentGetPage(link, agent=agent).addCallback(self.vidfast).addErrback(self.errorload)

			elif re.search('verystream\.com', data, re.S):
				if "/e/" in data:
					link = data
				else:
					vid = re.search('.*?/stream/(.*?)(?:/|$)', data, re.S)
					if vid:
						link = "https://verystream.com/e/" + vid.group(1)
					else:
						self.stream_not_found()
						return
				id = link.strip('/').rsplit('/')[-1]
				self.agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
				mp_globals.player_agent = self.agent
				self.referer = 'https://filmpalast.to'
				self.retry = 0
				twAgentGetPage(link, agent=self.agent, headers={'referer':self.referer}).addCallback(self.verystream, id, link).addErrback(self.errorload)

			elif re.search('vidlox(\.tv|\.me)', data, re.S):
				if re.search('vidlox(\.tv|\.me)/embed-', data, re.S):
					link = data
				else:
					id = re.search('vidlox(?:\.tv|\.me)/(\w+)', data)
					if id:
						link = "https://vidlox.tv/embed-%s.html" % id.group(1)
				if (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value) and not self.fallback:
					self.rdb = 1
					self.prz = 1
					self.callPremium(link)
				else:
					twAgentGetPage(link).addCallback(self.vidlox).addErrback(self.errorload)

			elif re.search('vidcloud\.co', data, re.S):
				fid = re.search('vidcloud\.co/embed/(.*?)/', data, re.S)
				if fid:
					link = "https://vidcloud.co/player?fid=%s&page=embed" % fid.group(1)
					agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
					mp_globals.player_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36 OPR/34.0.2036.50'
					twAgentGetPage(link, agent=agent).addCallback(self.vidcloud).addErrback(self.errorload)
				else:
					self.stream_not_found()

			elif re.search('streamango\.com|streamcherry\.com', data, re.S):
				link = data
				spezialagent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
				twAgentGetPage(link, agent=spezialagent).addCallback(self.streamango).addErrback(self.errorload)

			else:
				message = self.session.open(MessageBoxExt, _("No supported Stream Hoster, try another one!"), MessageBoxExt.TYPE_INFO, timeout=5)
		else:
			message = self.session.open(MessageBoxExt, _("Invalid Stream link, try another Stream Hoster!"), MessageBoxExt.TYPE_INFO, timeout=5)
		self.fallback = False

	def stream_not_found(self):
		message = self.session.open(MessageBoxExt, _("Stream not found, try another Stream Hoster."), MessageBoxExt.TYPE_INFO, timeout=5)

	def only_premium(self):
		if not (config_mp.mediaportal.premiumize_use.value or config_mp.mediaportal.realdebrid_use.value):
			message = self.session.open(MessageBoxExt, _("This hoster is only working with enabled Premium support."), MessageBoxExt.TYPE_INFO, timeout=5)
		else:
			message = self.session.open(MessageBoxExt, _("This Stream link is currently not available via Premium, try another Stream Hoster."), MessageBoxExt.TYPE_INFO, timeout=5)

	def errorload(self, error):
		printl('[streams]: ' + str(error),'','E')
		message = self.session.open(MessageBoxExt, _("Unknown error, check MP logfile."), MessageBoxExt.TYPE_INFO, timeout=5)