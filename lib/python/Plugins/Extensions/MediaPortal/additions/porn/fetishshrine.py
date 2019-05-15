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
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper

agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
default_cover = "file://%s/fetishshrine.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class fetishshrineGenreScreen(MPScreen):

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

		self['title'] = Label("FetishShrine.com")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "https://www.fetishshrine.com/categories/"
		twAgentGetPage(url, agent=agent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('class="thumbs-list">(.*?)$', data, re.S)
		if parse:
			Cats = re.findall('class="thumb".*?href="(.*?)"\stitle="(.*?)".*?img\ssrc="(.*?)"', parse.group(1), re.S)
			if Cats:
				for (Url, Title, Image) in Cats:
					self.genreliste.append((decodeHtml(Title), Url, Image))
		self.genreliste.sort()
		self.genreliste.insert(0, ("Most Viewed", "https://www.fetishshrine.com/most-popular/", default_cover))
		self.genreliste.insert(0, ("Top Rated", "https://www.fetishshrine.com/top-rated/", default_cover))
		self.genreliste.insert(0, ("Newest", "https://www.fetishshrine.com/latest-updates/", default_cover))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image, agent=agent)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(fetishshrineFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = urllib.quote(callback).replace(' ', '+')
			self.session.open(fetishshrineFilmScreen, Link, Name)

class fetishshrineFilmScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label("FetishShrine.com")
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
			url = "https://www.fetishshrine.com/search/%s/?q=%s" % (str(self.page), self.Link)
		else:
			if self.page > 1:
				url = "%s%s/" % (self.Link, str(self.page))
			else:
				url = "%s" % self.Link
		print url
		twAgentGetPage(url).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="paging">(.*?)</ul>')
		Movies = re.findall('class="thumb"\sitemscope.*?href="(.*?)".*?(?:img\ssrc|data-original)="(.*?)"\salt="(.*?)">(.*?)</div', data, re.S)
		if Movies:
			for (Url, Image, Title, Meta) in Movies:
				Runtime = '-'
				Views = '-'
				Age = '-'
				metadata = re.findall('class="length">(.*?)</span.*?class="views">(.*?)</span', Meta, re.S)
				if metadata:
					Runtime = metadata[0][0].strip()
					if "|" in metadata[0][1]:
						Views = metadata[0][1].split("|")[0].replace('Views','').strip()
						Age = metadata[0][1].split("|")[1].strip()
				self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views, Age))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		Url = self['liste'].getCurrent()[0][1]
		if Url == None:
			return
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		age = self['liste'].getCurrent()[0][5]
		self['name'].setText(title)
		self['handlung'].setText("Runtime: %s\nViews: %s\nAge: %s" % (runtime, views, age))
		CoverHelper(self['coverArt']).getCover(pic, agent=agent)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if not Link:
			return
		self.keyLocked = True
		twAgentGetPage(Link, agent=agent).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		videoPage = re.findall("video_url:\s'(.*?)',", data, re.S)
		if videoPage:
			self.keyLocked = False
			Title = self['liste'].getCurrent()[0][0]
			url = videoPage[-1]
			self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='fetishshrine')