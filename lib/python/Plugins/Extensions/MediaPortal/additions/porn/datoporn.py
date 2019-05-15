# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

myagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
default_cover = "file://%s/datoporn.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
base_url = "https://datoporn.co"

class datopornGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
		}, -1)

		self['title'] = Label("DatoPorn.com")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = base_url + "/categories_all"
		twAgentGetPage(url, agent=myagent, timeout=60).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('class="vid_block".*?href="(.*?)".*?class="link"><b>(.*?)</b', data, re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = base_url + "/?cat_name=%s&op=search&per_page=20&page=" % Url.split('/')[-1]
				Title = decodeHtml(Title.title().replace('Porn','').strip())
				self.genreliste.append((Title, Url))
		self.genreliste.sort()
		self.genreliste.insert(0, ("Featured", "FEATURED"))
		self.genreliste.insert(0, ("Most Viewed", "MOST VIEWED"))
		#self.genreliste.insert(0, ("Newest", "JUST ADDED"))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = urllib.quote(callback).replace(' ', '+')
			Name = "--- Search ---"
			Link = '%s' % (self.suchString)
			self.session.open(datopornFilmScreen, Link, Name)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(datopornFilmScreen, Link, Name)

class datopornFilmScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label("DatoPorn.com")
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
			url = base_url + "/?k=%s&op=search&per_page=20&page=%s" % (self.Link, str(self.page))
		else:
			if self.Link in ["FEATURED","MOST VIEWED","JUST ADDED"]:
				url = base_url
			else:
				url = self.Link + str(self.page)
		twAgentGetPage(url, agent=myagent, timeout=60).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		if self.Link in ["FEATURED","MOST VIEWED","JUST ADDED"]:
			data = re.search('class="first-word">%s(.*?)class="clear">' % self.Link, data, re.S).group(1)
		self.getLastPage(data, 'class="pagination(.*?)</div>')
		Movies = re.findall('class="videobox".*?href="(.*?)".*?background:\s{0,1}url\(\'(.*?)\'\).*?<span>(.*?)</span>.*?class="title">(.*?)</a>.*?class="views">(.*?)\sviews.*?class="date">(.*?)</span', data, re.S)
		if Movies:
			for (Url, Image, Runtime, Title, Views, Added) in Movies:
				self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views, Added))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		added = self['liste'].getCurrent()[0][5]
		self['handlung'].setText("Runtime: %s\nAdded: %s\nViews: %s" % (runtime, added, views))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, url):
		title = self['liste'].getCurrent()[0][0]
		mp_globals.player_agent = myagent
		self.session.open(SimplePlayer, [(title, url)], showPlaylist=False, ltype='datoporn')