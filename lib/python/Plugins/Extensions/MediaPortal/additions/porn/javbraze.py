# -*- coding: utf-8 -*-

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

myagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
default_cover = "file://%s/javbraze.png" % (config.mediaportal.iconcachepath.value + "logos")

class javbrazeGenreScreen(MPScreen):

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

		self['title'] = Label("JavBraze.com")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://javbraze.com/categories/"
		getPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('class="category".*?href="(.*?)".*?img\ssrc="(.*?)".*?title">(.*?)</div', data, re.S)
		if Cats:
			for (Url, Image, Title) in Cats:
				Url = 'http://javbraze.com/' + Url
				Image = 'http://javbraze.com/' + Image
				self.genreliste.append((Title, Url, Image, True))
		self.genreliste.sort()
		self.genreliste.insert(0, ("Being Watched", "http://javbraze.com/watched/", default_cover, False))
		self.genreliste.insert(0, ("Longest", "http://javbraze.com/longest/", default_cover, False))
		self.genreliste.insert(0, ("Most Downloaded", "http://javbraze.com/downloaded/", default_cover, False))
		self.genreliste.insert(0, ("Most Discussed", "http://javbraze.com/discussed/", default_cover, False))
		self.genreliste.insert(0, ("Top Rated", "http://javbraze.com/rated/", default_cover, False))
		self.genreliste.insert(0, ("Most Popular", "http://javbraze.com/popular/", default_cover, False))
		self.genreliste.insert(0, ("Most Recent", "http://javbraze.com/recent/", default_cover, False))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover, False))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			Name = "--- Search ---"
			Link = '%s' % (self.suchString)
			self.session.open(javbrazeFilmScreen, Link, Name, False)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			Cat = self['liste'].getCurrent()[0][3]
			self.session.open(javbrazeFilmScreen, Link, Name, Cat)

class javbrazeFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Cat):
		self.Link = Link
		self.Name = Name
		self.Cat = Cat
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

		self['title'] = Label("JavBraze.com")
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
			url = "http://javbraze.com/search/video/?s=%s&page=%s" % (self.Link, str(self.page))
		else:
			if self.page > 1:
				if self.Cat:
					cat = "recent/"
				else:
					cat = ""
				url = self.Link + cat + str(self.page) + "/"
			else:
				url = self.Link
		getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pagination(.*?)</ul>')
		Movies = re.findall('class="video".*?href="(.*?)"\stitle="(.*?)".*?img\ssrc="(.*?)".*?class="time-video.*?>(.*?)</span.*?class="video-view.*?>(.*?)\sviews', data, re.S)
		if Movies:
			for (Url, Title, Image, Runtime, Views) in Movies:
				Url = "http://javbraze.com" + Url
				Image = "http://javbraze.com" + Image
				Runtime = Runtime.strip()
				Views = Views.strip()
				self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, None, None))
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
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		self['handlung'].setText("Runtime: %s\nViews: %s" % (runtime, views))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		if url:
			self.keyLocked = True
			getPage(url, agent=myagent).addCallback(self.loadStream).addErrback(self.dataError)

	def loadStream(self, data):
		streams = re.findall('src="(/modules/video/player/config2.php\?id=\d+)"', data, re.S)
		if streams:
			url = "http://javbraze.com" + streams[0]
			getPage(url, agent=myagent).addCallback(self.get_link).addErrback(self.dataError)
		else:
			streams = re.findall('(?:src|href)=[\'|"](http[s]?://(?!(?:www.|m.|)javbraze.com)(.*?)\/.*?)[\'|"|\&|<]', data, re.S|re.I)
			if streams:
				for (stream, hostername) in streams:
					if isSupportedHoster(hostername, True):
						url = stream.replace('&amp;','&').replace('&#038;','&')
						get_stream_link(self.session).check_link(url, self.got_link)
		self.keyLocked = False

	def get_link(self, data):
		vid = re.findall("file':\s'(.*?)'", data, re.S)
		if vid:
			self.got_link(vid[-1])

	def got_link(self, stream_url):
		title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(title, stream_url)], showPlaylist=False, ltype='javbraze')