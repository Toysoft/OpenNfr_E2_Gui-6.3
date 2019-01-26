# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
default_cover = "file://%s/pornvortexx.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class PornVortexxGenreScreen(MPScreen):

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

		self['title'] = Label("PornVortexx.com")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = 'https://pornvortexx.com/browse.html'
		getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('<ul class="pm-ul-browse-categories thumbnails">(.*?)</ul>', data, re.S)
		cats = re.findall('<a href="(.*?)\d+-date.html">.*?<img src="(.*?)" alt=".*?" width=".*?">.*?<h3>(.*?)</h3>', parse.group(0), re.S)
		if cats:
			for (url, img, title) in cats:
				Title = title.replace(' ','').replace('\n','')
				self.genreliste.append((Title, url, img))
		self.genreliste.sort()
		self.genreliste.insert(0, ("Most Popular (All Time)", "https://pornvortexx.com/topvideos.html?page=", default_cover))
		self.genreliste.insert(0, ("Most Popular (Last 10 days)", "https://pornvortexx.com/topvideos.html?do=recent&page=", default_cover))
		self.genreliste.insert(0, ("Top Rated", "https://pornvortexx.com/topvideos.html?do=rating&page=", default_cover))
		self.genreliste.insert(0, ("Most Recent", "https://pornvortexx.com/newvideos.html?page=", default_cover))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(PornVortexxFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = '%s' % urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(PornVortexxFilmScreen, Link, Name)

class PornVortexxFilmScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label("PornVortexx.com")
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
		i = 0
		url = ''
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if ('Most Recent' or 'Most Popular' or 'Top Rated') in self.Name:
			url = "%s%s" % (self.Link, str(self.page))
		elif re.match(".*?Search", self.Name):
			url = "https://pornvortexx.com/search.php?keywords=%s&page=%s"  % (self.Link, str(self.page))
		else:
			url = "%s%s-date.html" % (self.Link, str(self.page))
		getPage(url).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, '<div class="pagination pagination-centered">(.*?)</div>')
		parse = re.search('<ul class="pm-ul-(?:browse|new|alltop)-videos thumbnails" id="pm-grid">(.*?)</ul>', data, re.S)
		if not parse:
			parse = re.search('<ul class="pm-ul-browse-videos pm-ul-browse-videos-ext thumbnails primary-extended" id="pm-grid">(.*?)</ul>', data, re.S)
		if parse:
			videos = re.findall('<div class="pm-li-video">.*?<a href="(.*?)" class=".*?"><span class="pm-thumb-fix-clip"><img src="(.*?)" alt="(.*?)" width=".*?">', parse.group(0), re.S)
			for (url, img, desc) in videos:
				self.filmliste.append((decodeHtml(desc), url, img))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][2]
		self['name'].setText(Title)
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			getPage(Link).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		videoPage = re.findall('<iframe src="(.*?)"', data, re.S|re.I)
		if videoPage:
			get_stream_link(self.session).check_link(str(videoPage[0]), self.got_link)

	def got_link(self, stream_url):
		Title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(Title, stream_url)], cover=False, showPlaylist=False, ltype='pornvortexx')