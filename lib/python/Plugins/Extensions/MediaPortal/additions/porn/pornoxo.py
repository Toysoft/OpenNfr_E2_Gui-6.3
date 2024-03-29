﻿# -*- coding: utf-8 -*-
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
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt

json_headers = {
	'Accept':'application/json',
	'Accept-Language':'en,en-US;q=0.7,en;q=0.3',
	'X-Requested-With':'XMLHttpRequest',
	'Content-Type':'application/x-www-form-urlencoded',
	}

myagent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11'

class pornoxoGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		global default_cover
		if self.mode == "pornoxo":
			self.portal = "PornoXO.com"
			self.baseurl = "https://www.pornoxo.com"
			default_cover = "file://%s/pornoxo.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "ashemaletube":
			self.portal = "aShemaletube.com"
			self.baseurl = "https://www.ashemaletube.com"
			default_cover = "file://%s/ashemaletube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "fetishpapa":
			self.portal = "Fetishpapa.com"
			self.baseurl = "https://www.fetishpapa.com"
			default_cover = "file://%s/fetishpapa.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel
		}, -1)

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "%s/tags/" % self.baseurl
		getPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('<div id="maincolumn2"(.*?)$', data, re.S)
		Cats = re.findall('href="(/videos/.*?)(?:most-popular/today/|)".*?class="tag-item.*?>(.*?)<span', parse.group(1), re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = self.baseurl + Url + "newest/"
				self.genreliste.append((Title.strip(), Url))
			self.genreliste.sort()
			self.genreliste.insert(0, ("Longest", "%s/videos/longest/" % self.baseurl, None))
			self.genreliste.insert(0, ("Best Recent", "%s/videos/best-recent/" % self.baseurl, None))
			self.genreliste.insert(0, ("Top Rated", "%s/videos/top-rated/" % self.baseurl, None))
			self.genreliste.insert(0, ("Most Popular", "%s/videos/most-popular/today/" % self.baseurl, None))
			self.genreliste.insert(0, ("Most Recent", "%s/videos/newest/" % self.baseurl, None))
			self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.keyLocked = False

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = '%s' % urllib.quote(self.suchString).replace(' ', '_')
			self.session.open(pornoxoFilmScreen, Link, Name, self.portal, self.baseurl)

	def getSuggestions(self, text, max_res):
		url = "%s/main-search.html?categoryValue=1&term=%s" % (self.baseurl, urllib.quote_plus(text))
		d = twAgentGetPage(url, agent=myagent, headers=json_headers, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, err=True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and type(suggestions) in (str, buffer):
			suggestions = json.loads(suggestions)
			for item in suggestions["keyword"]:
				li = item
				list.append(str(li))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen(suggest_func=self.getSuggestions)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(pornoxoFilmScreen, Link, Name, self.portal, self.baseurl)

class pornoxoFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl

		global default_cover
		if self.portal == "PornoXO.com":
			default_cover = "file://%s/pornoxo.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "aShemaletube.com":
			default_cover = "file://%s/ashemaletube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "Fetishpapa.com":
			default_cover = "file://%s/fetishpapa.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "%s/search/%s/page%s.html" % (self.baseurl, self.Link, str(self.page))
		else:
			url = self.Link + str(self.page) + '/'
		getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pagination(.*?)</div>')
		parse = re.search('(.*?)class="top-tags-box"', data, re.S)
		Movies = re.findall('vidItem"\sdata-video-id="\d+">.{1,10}(?:<div class="thumb-inner-wrapper">|).*?<a\shref="(.*?)"\s{0,1}>.{0,10}<img\ssrc="(.*?)"\salt="(.*?)"', parse.group(1), re.S)
		if Movies:
			for (Url, Image, Title) in Movies:
				if Url.startswith('/'):
					Url = self.baseurl + Url
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)
		Url = self['liste'].getCurrent()[0][1]
		pic = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		if url:
			getPage(url).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		url = re.findall('"src":"(.*?)"', data, re.S)
		if url:
			self.keyLocked = False
			title = self['liste'].getCurrent()[0][0]
			self.session.open(SimplePlayer, [(title, url[0].replace('\/','/'))], showPlaylist=False, ltype='pornoxo')