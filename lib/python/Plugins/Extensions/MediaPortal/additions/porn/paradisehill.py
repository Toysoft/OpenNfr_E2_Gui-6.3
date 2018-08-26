# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
default_cover = "file://%s/paradisehill.png" % (config.mediaportal.iconcachepath.value + "logos")

class paradisehillGenreScreen(MPScreen):

	def __init__(self, session):

		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self.language = "de"
		self.suchString = ''
		self['title'] = Label("ParadiseHill")
		self['ContentTitle'] = Label("Genres")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://en.paradisehill.cc/categories/"
		getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('<div id="w0" class="content">(.*?)<script type="', data, re.S)
		Cat = re.findall('class="item".*?href="(.*?)".*?itemprop="name"><span>(.*?)</span>', parse.group(1), re.S)
		if Cat:
			for (Url, Title) in Cat:
				Url = Url + "&page="
				self.genreliste.append((Title, Url))
			self.genreliste.sort()
		self.genreliste.insert(0, ("Popular (All Time)", "/popular/?filter=all&sort=by_likes&page="))
		self.genreliste.insert(0, ("Popular (Year)", "/popular/?filter=year&sort=by_likes&page="))
		self.genreliste.insert(0, ("Popular (Monthly)", "/popular/?filter=month&sort=by_likes&page="))
		self.genreliste.insert(0, ("Popular (Weekly)", "/popular/?filter=week&sort=by_likes&page="))
		self.genreliste.insert(0, ("Popular (Daily)", "/popular/?filter=day&sort=by_likes&page="))
		self.genreliste.insert(0, ("Newest", "/all/?sort=created_at&page="))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			paradisehillUrl = '%s' % (self.suchString)
			paradisehillGenre = "--- Search ---"
			self.session.open(paradisehillFilmListeScreen, paradisehillUrl, paradisehillGenre)

	def keyOK(self):
		if self.keyLocked:
			return
		paradisehillGenre = self['liste'].getCurrent()[0][0]
		paradisehillUrl = self['liste'].getCurrent()[0][1]
		if paradisehillGenre == "--- Search ---":
			self.suchen()
		else:
			self.session.open(paradisehillFilmListeScreen, paradisehillUrl, paradisehillGenre)

class paradisehillFilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName):
		self.genreLink = genreLink
		self.genreName = genreName
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self['title'] = Label("ParadiseHill")
		self['ContentTitle'] = Label("Genre: %s" % self.genreName)
		self['name'] = Label("Film Auswahl")
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		if re.match(".*?Search", self.genreName):
			if self.page == 1:
				url = "http://en.paradisehill.cc/search/?pattern=%s&what=1" % self.genreLink
			else:
				url = "http://en.paradisehill.cc/search/?pattern=%s&what=1&page=%s" % (self.genreLink,str(self.page))
		else:
			url = "http://en.paradisehill.cc%s%s" % (self.genreLink,str(self.page))
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.getLastPage(data, 'class="pagination(.*?)</div>' , '.*page=(\d+)"')
		movies = re.findall('list-film-item.*?href="(.*?)".*?temprop="name">(.*?)</.*?</span>.*?img\ssrc="(.*?)"', data, re.S)
		if movies:
			self.filmliste = []
			for (url,title,image) in movies:
				url = "http://en.paradisehill.cc%s" % url
				image = "http://en.paradisehill.cc%s" % image
				self.filmliste.append((decodeHtml(title), url, image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste,0,1,2,None,None,self.page,self.lastpage)
		self.showInfos()

	def showInfos(self):
		streamTitle = self['liste'].getCurrent()[0][0]
		streamUrl = self['liste'].getCurrent()[0][1]
		streamPic = self['liste'].getCurrent()[0][2]
		self['name'].setText(streamTitle)
		CoverHelper(self['coverArt']).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		title = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		self.session.open(paradisehillFilmAuswahlScreen, title, url, image)

class paradisehillFilmAuswahlScreen(MPScreen):

	def __init__(self, session, genreName, genreLink, cover):
		self.genreLink = genreLink
		self.genreName = genreName
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("ParadiseHill")
		self['ContentTitle'] = Label("Streams")
		self['name'] = Label(self.genreName)

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		getPage(self.genreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('class="fp-playlist">(.*?)</div>', data, re.S)
		if parse:
			streams = re.findall('href="(.*?)">', parse.group(1), re.S)
		if len(streams) > 1:
			for i in range(0,len(streams),1):
				videoname = self.genreName + ' (Part ' + str(i+1) + ')'
				self.filmliste.append((videoname, streams[i]))
		elif len(streams) == 1:
			videoname = self.genreName
			self.filmliste.append((videoname, streams[0]))
		else:
			self.filmliste.append(("No streams found!",None))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink == None:
			return
		url = streamLink
		url = url.replace('&amp;','&').replace('&#038;','&')
		title = self.genreName
		mp_globals.player_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
		self.session.open(SimplePlayer, [(title, url, self.cover)], showPlaylist=False, ltype='paradisehill', cover=True)