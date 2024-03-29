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
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage

IPhone5Agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
MyHeaders= {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language':'en-US,en;q=0.5'}
default_cover = "file://%s/beeg.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

beeg_apikey = ''

class beegGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("beeg.com")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.getApiKeys)

	def getApiKeys(self):
		url = "https://beeg.com/"
		twAgentGetPage(url, agent=IPhone5Agent, headers=MyHeaders).addCallback(self.getApiKeys2).addErrback(self.dataError)

	def getApiKeys2(self, data):
		cpl = re.findall('beeg_version = (\d+);', data, re.S)
		global beeg_apikey
		beeg_apikey = cpl[0]
		url = "https://beeg.com/api/v6/%s/index/main/0/mobile" % beeg_apikey
		twAgentGetPage(url, agent=IPhone5Agent, headers=MyHeaders).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('"tags":\[(.*?)\]', data, re.S)
		if parse:
			Cats = re.findall('"tag":"(.*?)"', parse.group(1), re.S)
			if Cats:
				for Title in Cats:
					Url = 'https://beeg.com/api/v6/%s/index/tag/$PAGE$/mobile?tag=%s' % (beeg_apikey, Title)
					Title = Title.title()
					self.genreliste.append((Title, Url))
			self.genreliste.sort()
			self.genreliste.insert(0, ("Longest", "https://beeg.com/api/v6/%s/index/tag/$PAGE$/mobile?tag=long%svideos" % (beeg_apikey, "%20")))
			self.genreliste.insert(0, ("Newest", "https://beeg.com/api/v6/%s/index/main/$PAGE$/mobile" % beeg_apikey))
			#self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.keyLocked = False
		else:
			message = self.session.open(MessageBoxExt, _("Broken URL parsing, please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(beegFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = urllib.quote(callback).replace(' ', '+')
			Link = self.suchString
			Name = "--- Search ---"
			self.session.open(beegFilmScreen, Link, Name)

class beegFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name

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

		self['title'] = Label("beeg.com")
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
		if re.match(".*Search", self.Name):
			url = 'https://beeg.com/api/v6/%s/index/search/$PAGE$/mobile?query=%s' % (beeg_apikey, self.Link)
			url = url.replace('$PAGE$', '%s' % str(self.page-1))
		else:
			url = self.Link.replace('$PAGE$', '%s' % str(self.page-1))
		twAgentGetPage(url, agent=IPhone5Agent, headers=MyHeaders).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, '', '"pages":(.*?),')
		Videos = re.findall('\{"title":"(.*?)","id":(\d+)', data, re.S)
		if Videos:
			for (Title, VideoId) in Videos:
				Url = 'https://beeg.com/api/v6/%s/video/%s' % (beeg_apikey, VideoId)
				Image = 'https://img.beeg.com/800x450/%s.jpg' % VideoId
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		twAgentGetPage(url, agent=IPhone5Agent, headers=MyHeaders).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		streamlinks = re.findall('\d{3}p":"(.*?)"', data , re.S)
		if streamlinks:
			streamlink = streamlinks[-1].replace('/{DATA_MARKERS}/', '/data=pc_XX__%s/' % beeg_apikey)
			if streamlink.startswith('//'):
				streamlink = "http:" + streamlink
			Title = self['liste'].getCurrent()[0][0]
			Cover = self['liste'].getCurrent()[0][2]
			mp_globals.player_agent = IPhone5Agent
			self.session.open(SimplePlayer, [(Title, streamlink, Cover)], showPlaylist=False, ltype='beeg', cover=True)
		else:
			message = self.session.open(MessageBoxExt, _("Stream not found"), MessageBoxExt.TYPE_INFO, timeout=3)