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
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

class porntvGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		global default_cover
		if self.mode == "porntv":
			self.portal = "PornTV.com"
			self.baseurl = "https://www.porntv.com"
			default_cover = "file://%s/porntv.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "youngpornvideos":
			self.portal = "YoungPornVideos.com"
			self.baseurl = "https://www.youngpornvideos.com"
			default_cover = "file://%s/youngpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "ghettotube":
			self.portal = "GhettoTube.com"
			self.baseurl = "https://www.ghettotube.com"
			default_cover = "file://%s/ghettotube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "teenieporn":
			self.portal = "TeeniePorn.com"
			self.baseurl = "https://www.teenieporn.com"
			default_cover = "file://%s/teenieporn.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "asianpornmovies":
			self.portal = "AsianPornMovies.com"
			self.baseurl = "https://www.asianpornmovies.com"
			default_cover = "file://%s/asianpornmovies.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "cartoonpornvideos":
			self.portal = "CartoonPornVideos.com"
			self.baseurl = "https://www.cartoonpornvideos.com"
			default_cover = "file://%s/cartoonpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "lesbianpornvideos":
			self.portal = "LesbianPornVideos.com"
			self.baseurl = "https://www.lesbianpornvideos.com"
			default_cover = "file://%s/lesbianpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "sexoasis":
			self.portal = "SexOasis.com"
			self.baseurl = "https://www.sexoasis.com"
			default_cover = "file://%s/sexoasis.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "asspoint":
			self.portal = "AssPoint.com"
			self.baseurl = "https://www.asspoint.com"
			default_cover = "file://%s/asspoint.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "analpornvideos":
			self.portal = "AnalPornVideos.com"
			self.baseurl = "https://www.analpornvideos.com"
			default_cover = "file://%s/analpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "hoodtube":
			self.portal = "HoodTube.com"
			self.baseurl = "https://www.hoodtube.com"
			default_cover = "file://%s/hoodtube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "bigboobstube":
			self.portal = "BigBoobsTube.com"
			self.baseurl = "https://www.bigboobstube.com"
			default_cover = "file://%s/bigboobstube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "suzisporn":
			self.portal = "SuzisPorn.com"
			self.baseurl = "https://www.suzisporn.com"
			default_cover = "file://%s/suzisporn.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "movieshark":
			self.portal = "MovieShark.com"
			self.baseurl = "https://www.movieshark.com"
			default_cover = "file://%s/movieshark.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "youngsextube":
			self.portal = "YoungSexTube.com"
			self.baseurl = "https://www.youngsextube.com"
			default_cover = "file://%s/youngsextube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "youngporno":
			self.portal = "YoungPorno.com"
			self.baseurl = "https://www.youngporno.com"
			default_cover = "file://%s/youngporno.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "porntitan":
			self.portal = "PornTitan.com"
			self.baseurl = "https://www.porntitan.com"
			default_cover = "file://%s/porntitan.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "xjizz":
			self.portal = "XJizz.com"
			self.baseurl = "https://www.xjizz.com"
			default_cover = "file://%s/xjizz.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "movietitan":
			self.portal = "MovieTitan.com"
			self.baseurl = "https://www.movietitan.com"
			default_cover = "file://%s/movietitan.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "cartoonsextube":
			self.portal = "CartoonSexTube.com"
			self.baseurl = "https://www.cartoonsextube.com"
			default_cover = "file://%s/cartoonsextube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "mobilepornmovies":
			self.portal = "MobilePornMovies.com"
			self.baseurl = "https://www.mobilepornmovies.com"
			default_cover = "file://%s/mobilepornmovies.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "xxxmilfs":
			self.portal = "XXXMilfs.com"
			self.baseurl = "https://www.xxxmilfs.com"
			default_cover = "file://%s/xxxmilfs.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
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
		self['name'].setText(_('Please wait...'))
		url = "%s/categories/?preference=1" % self.baseurl
		getPage(url, agent=agent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('<h1>Popular Categories</h1>(.*?)<h1>', data, re.S)
		if not parse:
			parse = re.search('class="universalheader">(.*?)$', data, re.S)
			if not parse:
				parse = re.search('id="load">(.*?)$', data, re.S)
		Cats = re.findall('(?:class="item"|<div style=).*?href="(.*?)">(?:<font size=3><b>|)(.*?)(?:</a|</b></font>).*?(?:cat-img"|img).src="(.*?)"', parse.group(1), re.S)
		if Cats:
			for (Url, Title, Image) in Cats:
				if Url.endswith('.html'):
					Url = Url.replace('-popular.html','-recent.html').split('.html')[0] + "-$$PAGE$$.html"
					if Url.startswith('/'):
						Url = self.baseurl + Url
				if self.mode == "porntitan":
					Title = Title.split(' Porn')[0]
				self.genreliste.append((Title.title(), Url, Image))
			self.genreliste.sort()
		self.genreliste.insert(0, ("Longest", "%s/videos/straight/all-length-$$PAGE$$.html" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Top Rated", "%s/videos/straight/all-rate-$$PAGE$$.html" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Most Viewed", "%s/videos/straight/all-view-$$PAGE$$.html" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Most Popular", "%s/videos/straight/all-popular-$$PAGE$$.html" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Most Recent", "%s/videos/straight/all-recent-$$PAGE$$.html" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = '%s' % urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(porntvFilmScreen, Link, Name, self.portal, self.baseurl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(porntvFilmScreen, Link, Name, self.portal, self.baseurl)

class porntvFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl

		global default_cover
		if self.portal == "PornTV.com":
			default_cover = "file://%s/porntv.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "YoungPornVideos.com":
			default_cover = "file://%s/youngpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "GhettoTube.com":
			default_cover = "file://%s/ghettotube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "TeeniePorn.com":
			default_cover = "file://%s/teenieporn.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "AsianPornMovies.com":
			default_cover = "file://%s/asianpornmovies.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "CartoonPornVideos.com":
			default_cover = "file://%s/cartoonpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "LesbianPornVideos.com":
			default_cover = "file://%s/lesbianpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "SexOasis.com":
			default_cover = "file://%s/sexoasis.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "AssPoint.com":
			default_cover = "file://%s/asspoint.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "AnalPornVideos.com":
			default_cover = "file://%s/analpornvideos.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "HoodTube.com":
			default_cover = "file://%s/hoodtube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "BigBoobsTube.com":
			default_cover = "file://%s/bigboobstube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "SuzisPorn.com":
			default_cover = "file://%s/suzisporn.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "MovieShark.com":
			default_cover = "file://%s/movieshark.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "YoungSexTube.com":
			default_cover = "file://%s/youngsextube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "YoungPorno.com":
			default_cover = "file://%s/youngporno.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "PornTitan.com":
			default_cover = "file://%s/porntitan.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "XJizz.com":
			default_cover = "file://%s/xjizz.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "MovieTitan.com":
			default_cover = "file://%s/movietitan.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "CartoonSexTube.com":
			default_cover = "file://%s/cartoonsextube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "MobilePornMovies.com":
			default_cover = "file://%s/mobilepornmovies.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "XXXMilfs.com":
			default_cover = "file://%s/xxxmilfs.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

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
			url = "%s/search/video/%s/%s/" % (self.baseurl, self.Link, str(self.page))
		else:
			url = self.Link.replace('$$PAGE$$',str(self.page))
		getPage(url, agent=agent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, '(?:class="pagination"|class="pages2">)(.*?)</div>')
		Items = re.findall('class="(?:item"|thumb"|group)(.*?(?:clock.*?</span>|infoBox.*?</div>|class="ago">.*?</div>|Views: <strong>.*?</p>))', data, re.S)
		for item in Items:
			Movies = re.findall('href="(.*?)".*?img(?: class="pop-execute"|)\ssrc="(.*?)"\swidth="\d+"\sheight="\d+".*?alt="(.*?)"(.*?clock.*?</span>|.*?infoBox.*?</div>|.*?class="ago">.*?</div>|.*?Views: <strong>.*?</p>)', item, re.S)
			if Movies:
				for (Url, Image, Title, Meta) in Movies:
					if "infoBox" in Meta:
						info = re.findall('<span>(.*?)</span> \| <span>(.*?) Views</span> \| <span>(.*?)</span>', Meta, re.S)
						for (Runtime, Views, Date) in info:
							if Url.startswith('/'):
								Url = self.baseurl + Url
						self.filmliste.append((decodeHtml(Title), Url, Image, '', Date, Views, Runtime))
					elif 'class="ago">' in Meta:
						info = re.findall('class="lenght">(.*?)</p.*?class="views">(.*?)<span.*?class="ago">(.*?)</p', Meta, re.S)
						for (Runtime, Views, Date) in info:
							if Url.startswith('/'):
								Url = self.baseurl + Url
						self.filmliste.append((decodeHtml(Title), Url, Image, '', Date, Views, Runtime))
					elif 'class="gg-desc">' in Meta:
						info = re.findall('Time:\s<strong><span>(.*?)</span.*?Added:\s<span>(.*?)</span.*?Views:\s<strong><span>(.*?)</span', Meta, re.S)
						for (Runtime, Views, Date) in info:
							if Url.startswith('/'):
								Url = self.baseurl + Url
						self.filmliste.append((decodeHtml(Title), Url, Image, '', Date, Views, Runtime))
					else:
						Rating = re.findall('like"></use></svg>(.*?)</span>', Meta, re.S)
						Date = re.findall('calendar"></use></svg>(.*?)</span>', Meta, re.S)
						Views = re.findall('eye"></use></svg>(.*?)</span>', Meta, re.S)
						Runtime = re.findall('clock"></use></svg>(.*?)</span>', Meta, re.S)
						if Url.startswith('/'):
							Url = self.baseurl + Url
						self.filmliste.append((decodeHtml(Title), Url, Image, Rating[0], Date[0], Views[0], Runtime[0]))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, '', '', '', ''))
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
		rating = self['liste'].getCurrent()[0][3]
		added = self['liste'].getCurrent()[0][4]
		views = self['liste'].getCurrent()[0][5]
		runtime = self['liste'].getCurrent()[0][6]
		if rating:
			self['handlung'].setText("Runtime: %s\nViews: %s\nAdded: %s\nRating: %s" % (runtime, views, added, rating))
		else:
			self['handlung'].setText("Runtime: %s\nViews: %s\nAdded: %s" % (runtime, views, added))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		if url:
			getPage(url).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		url = re.findall('file:\s"(.*?)",.*?label:\s"\d+p', data, re.S)
		if url:
			self.keyLocked = False
			title = self['liste'].getCurrent()[0][0]
			self.session.open(SimplePlayer, [(title, url[0])], showPlaylist=False, ltype='porntv')