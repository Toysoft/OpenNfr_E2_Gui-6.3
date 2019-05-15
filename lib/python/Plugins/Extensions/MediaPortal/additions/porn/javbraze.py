# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

myagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'

class javbrazeGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		global default_cover
		if self.mode == "javbraze":
			self.portal = "JavBraze.com"
			self.baseurl = "https://www.javbraze.com"
			default_cover = "file://%s/javbraze.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javfindx":
			self.portal = "JavFindX.com"
			self.baseurl = "https://www.javfindx.com"
			default_cover = "file://%s/javfindx.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "pornbraze":
			self.portal = "PornBraze.com"
			self.baseurl = "https://www.pornbraze.com"
			default_cover = "file://%s/pornbraze.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "alotav":
			self.portal = "AlotAv.com"
			self.baseurl = "https://www.alotav.com"
			default_cover = "file://%s/alotav.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javfuq":
			self.portal = "JavFuq.com"
			self.baseurl = "https://www.javfuq.com"
			default_cover = "file://%s/javfuq.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javhd":
			self.portal = "JavHD.today"
			self.baseurl = "https://www.javhd.today"
			default_cover = "file://%s/javhd.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javboob":
			self.portal = "JavBoob.com"
			self.baseurl = "https://www.javboob.com"
			default_cover = "file://%s/javboob.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javmeta":
			self.portal = "JavMeta.com"
			self.baseurl = "https://www.javmeta.com"
			default_cover = "file://%s/javmeta.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javfinder":
			self.portal = "JavFinder.us"
			self.baseurl = "https://www.javfinder.us"
			default_cover = "file://%s/javfinder.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javbs":
			self.portal = "JavBs.com"
			self.baseurl = "https://www.javbs.com"
			default_cover = "file://%s/javbs.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

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
		url = "%s/categories/" % self.baseurl
		twAgentGetPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('class="category".*?href="(.*?)".*?img\s(?:style="width: 277px;height: 155px;"\s|)src="(.*?)".*?title">(.*?)</div', data, re.S)
		if Cats:
			for (Url, Image, Title) in Cats:
				Url = self.baseurl + '/' + Url
				if self.mode == "alotav" and "-" in Title:
					Title = Title.split('-')[0].strip()
				if Image.startswith('/'):
					Image = self.baseurl + Image
				self.genreliste.append((decodeHtml(Title), Url, Image, True))
		if self.mode == "javbraze":
			self.genreliste.append(("Uncensored", "%s/tag/uncen/" % self.baseurl, default_cover, False))
		elif self.mode == "pornbraze":
			self.genreliste.append(("Uncensored", "%s/jav-uncensored/" % self.baseurl, default_cover, True))
		self.genreliste.sort()
		self.genreliste.insert(0, ("Being Watched", "%s/watched/" % self.baseurl, default_cover, False))
		self.genreliste.insert(0, ("Longest", "%s/longest/" % self.baseurl, default_cover, False))
		self.genreliste.insert(0, ("Most Downloaded", "%s/downloaded/" % self.baseurl, default_cover, False))
		self.genreliste.insert(0, ("Most Discussed", "%s/discussed/" % self.baseurl, default_cover, False))
		self.genreliste.insert(0, ("Top Rated", "%s/rated/" % self.baseurl, default_cover, False))
		self.genreliste.insert(0, ("Most Popular", "%s/popular/" % self.baseurl, default_cover, False))
		self.genreliste.insert(0, ("Most Recent", "%s/recent/" % self.baseurl, default_cover, False))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover, False))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = urllib.quote(callback).replace(' ', '+')
			Name = "--- Search ---"
			Link = '%s' % (self.suchString)
			self.session.open(javbrazeFilmScreen, Link, Name, False, self.portal, self.baseurl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			Cat = self['liste'].getCurrent()[0][3]
			self.session.open(javbrazeFilmScreen, Link, Name, Cat, self.portal, self.baseurl)

class javbrazeFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Cat, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.Cat = Cat
		self.portal = portal
		self.baseurl = baseurl

		global default_cover
		if self.portal == "JavBraze.com":
			default_cover = "file://%s/javbraze.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "JavFindX.com":
			default_cover = "file://%s/javfindx.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "PornBraze.com":
			default_cover = "file://%s/pornbraze.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "AlotAv.com":
			default_cover = "file://%s/alotav.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "JavFuq.com":
			default_cover = "file://%s/javfuq.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "JavHD.today":
			default_cover = "file://%s/javhd.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "JavBoob.com":
			default_cover = "file://%s/javboob.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "JavMeta.com":
			default_cover = "file://%s/javmeta.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "JavFinder.us":
			default_cover = "file://%s/javfinder.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "JavBs.com":
			default_cover = "file://%s/javbs.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

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
			url = "%s/search/video/?s=%s&page=%s" % (self.baseurl, self.Link, str(self.page))
		else:
			if self.page > 1:
				if self.Cat:
					cat = "recent/"
				else:
					cat = ""
				url = self.Link + cat + str(self.page) + "/"
			else:
				url = self.Link
		twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pagination(.*?)</ul>')
		parse = re.search('<div class="panel-body(.*?)$', data, re.S)
		Movies = re.findall('(?:class="video">|class="well well-sm">).*?href="(.*?)"\stitle="(.*?)".*?img\s(?:class="img-responsive\s"\s|)src="(.*?)"(.*?(?:</div>(?:.|\n\t+)</li>|</span>.</div>))', parse.group(1), re.S)
		if Movies:
			for (Url, Title, Image, Meta) in Movies:
				Url = self.baseurl + Url
				Image = Image.replace('&amp;','&')
				if Image.startswith('/'):
					Image = self.baseurl + Image
				Runtime = re.findall('(?:class="time-video|class="video-overlay).*?>(.*?)</span', Meta, re.S)
				if Runtime:
					Runtime = Runtime[0].replace('HD','').strip()
				else:
					Runtime = "-"
				Added = re.findall('(?:class="video-view|class="pull-left).*?>(.*?)(?:</span>|</a>)', Meta, re.S)
				if Added:
					Added = stripAllTags(Added[0]).strip()
				else:
					Added = None
				Views = re.findall('(?:class="pull-right).*?>(.*?)(?:</span>|</a>)', Meta, re.S)
				if Views:
					Views = Views[0].replace('views','').replace('view','').strip()
				else:
					if Added and "view" in Added:
						Views = Added.replace('views','').replace('view','').strip()
						Added = None
					else:
						Views = None
				self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Added, Views))
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
		Url = self['liste'].getCurrent()[0][1]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		added = self['liste'].getCurrent()[0][4]
		views = self['liste'].getCurrent()[0][5]
		meta = "Runtime: %s" % runtime
		if views:
			meta = meta + "\nViews: %s" % views
		if added:
			meta = meta + "\nAdded: %s" % added
		self['handlung'].setText(meta)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		if url:
			self.keyLocked = True
			twAgentGetPage(url, agent=myagent).addCallback(self.loadStream).addErrback(self.dataError)

	def loadStream(self, data):
		streams = re.findall('<iframe.*?src="(https://(?:www.fembed.com|kissmovies.cc|smartshare.tv|vcdn.io)/v/.*?)\s{0,1}"', data, re.S)
		if streams:
			get_stream_link(self.session).check_link(streams[0], self.got_link)
		else:
			streams = re.findall('src="(/modules/video/player/config2.php\?id=\d+)"', data, re.S)
			if streams:
				url = self.baseurl + streams[0]
				twAgentGetPage(url, agent=myagent).addCallback(self.get_link).addErrback(self.dataError)
			else:
				streams = re.findall('(?:src|href)=[\'|"](http[s]?://(?!(?:www.|m.|)javbraze.com|javfindx.com|pornbraze.com|alotav.com|javfuq.com|javhd.today|javboob.com|javmeta.com|javfinder.us|javbs.com)(.*?)\/.*?)[\'|"|\&|<]', data, re.S|re.I)
				if streams:
					for (stream, hostername) in streams:
						check = isSupportedHoster(hostername)
						if check:
							url = stream.replace('&amp;','&').replace('&#038;','&')
							get_stream_link(self.session).check_link(url, self.got_link)
		self.keyLocked = False

	def got_link(self, stream_url):
		title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(title, stream_url)], showPlaylist=False, ltype='javbraze')