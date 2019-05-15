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
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt

agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
default_cover = None
cookies = CookieJar()

class pinflixGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		global default_cover
		if self.mode == "pinflix":
			self.portal = "Pinflix.com"
			self.baseurl = "https://www.pinflix.com"
			default_cover = "file://%s/pinflix.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "pornhd":
			self.portal = "PornHD.com"
			self.baseurl = "https://www.pornhd.com"
			default_cover = "file://%s/pornhd.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "pornrox":
			self.portal = "Pornrox.com"
			self.baseurl = "https://www.pornrox.com"
			default_cover = "file://%s/pornrox.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

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
		url = "%s/category" % self.baseurl
		twAgentGetPage(url, agent=agent, cookieJar=cookies).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('class="(?:category|pfx-cat)"><a href="(.*?)".*?alt="(.*?)".*?data-original="(.*?)"', data, re.S)
		if Cats:
			for (Url, Title, Image) in Cats:
				Url = self.baseurl + Url
				self.genreliste.append((Title, Url, Image))
		self.genreliste.sort()
		if not self.mode == "pinflix":
			self.genreliste.insert(0, ("Channels", "%s/channel" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Pornstars", "%s/pornstars" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Longtest", "%s/?order=longest" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Featured", "%s/?order=featured" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Top Rated", "%s/?order=top-rated" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Most Viewed", "%s/?order=most-popular" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("Newest", "%s/?order=newest" % self.baseurl, default_cover))
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
		elif Name == "Channels" or Name == "Pornstars":
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(pinflixSitesScreen, Link, Name, self.portal, self.baseurl)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(pinflixFilmScreen, Link, Name, self.portal, self.baseurl)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(pinflixFilmScreen, Link, Name, self.portal, self.baseurl)

class pinflixSitesScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl
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
			"green" : self.keyPageNumber,
			"yellow" : self.keySort
		}, -1)

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		self['F3'] = Label(_("Sort"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.sort = 'most-popular'
		self.sorttext = 'Most Popular'

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		url = "%s?order=%s&page=%s" % (self.Link, self.sort, str(self.page))
		twAgentGetPage(url, agent=agent, cookieJar=cookies).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'paging">(.*?)</ul>')
		Movies = re.findall('class="(?:pfx-pornstar|pornstar)"><a href="(.*?)".*?data-original="(.*?)".*?alt="(.*?)"', data, re.S)
		if Movies:
			for (Url, Image, Title) in Movies:
				Url = self.baseurl + Url
				self.filmliste.append((decodeHtml(Title), Url, Image))
		else:
			parse = re.search('class="jsFilter(.*?)class="page-footer"', data, re.S)
			Movies = re.findall('<li><a href="(.*?)".*?img\ssrc="(.*?)"\salt="(.*?)"', parse.group(1), re.S)
			if Movies:
				for (Url, Image, Title) in Movies:
					Url = self.baseurl + Url
					if "placeholder" in Image:
						Image = default_cover
					self.filmliste.append((decodeHtml(Title), Url, Image))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage)
		self.showInfos()
		self.keyLocked = False

	def keySort(self):
		if self.keyLocked:
			return
		if self.Name == 'Pornstars':
			rangelist = [['Most Popular', 'most-popular'], ['Most Videos','video-count'], ['Alphabetical','alphabetical']]
		else:
			rangelist = [['Most Popular', 'most-popular'], ['Most Videos','video-count'], ['Alphabetical','alphabetical'], ['Newest','newest']]
		self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keySortAction(self, result):
		if result:
			self.sort = result[1]
			self.sorttext = result[0]
			self.loadPage()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][2]
		self['handlung'].setText("%s: %s" % (_("Sort order"),self.sorttext))
		self['name'].setText(Title)
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(pinflixFilmScreen, Link, Name, self.portal, self.baseurl)

class pinflixFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl

		global default_cover
		if self.portal == "Pinflix.com":
			default_cover = "file://%s/pinflix.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "PornHD.com":
			default_cover = "file://%s/pornhd.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "Pornrox.com":
			default_cover = "file://%s/pornrox.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

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
			"green" : self.keyPageNumber,
			"yellow" : self.keySort
		}, -1)

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		self['F3'] = Label(_("Sort"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		if re.match(".*?Search", self.Name):
			self.sort = 'mostrelevant'
			self.sorttext = 'Most Relevant'
		else:
			self.sort = 'newest'
			self.sorttext = 'Newest'

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "%s/search?search=%s&order=%s&page=%s" % (self.baseurl, self.Link, self.sort, str(self.page))
		else:
			sortpart = re.findall('^(.*?)\?order=(.*?)$', self.Link)
			if sortpart:
				self.Link = sortpart[0][0]
				self.sort = sortpart[0][1]
			url = "%s?order=%s&page=%s" % (self.Link, self.sort, str(self.page))
		twAgentGetPage(url, agent=agent, cookieJar=cookies).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		if "data-last-page=" in data:
			self.getLastPage(data, '', 'data-last-page="(\d+)"')
		else:
			self.getLastPage(data, 'paging">(.*?)</ul>')
		Movies = re.findall('class="thumb(?: videoThumb|)(?: popTrigger|)"\shref="(/videos.*?)"><img\salt="(.*?)"\s+src="(.*?)"(\sclass="(?:pfx-|)lazy"\sdata-original=".*?"|).*?class="meta transition"><time>(.*?)</time', data, re.S)
		if Movies:
			for (Url, Title, Image, BackupImage, Runtime) in Movies:
				Url = self.baseurl + Url
				Image = Image.replace('.webp','.jpg')
				if BackupImage:
					Image = re.search('data-original="(.*?)"', BackupImage, re.S).group(1).replace('.webp','.jpg')
				self.filmliste.append((decodeHtml(Title).strip(), Url, Image, Runtime))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.ml.moveToIndex(0)
			self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
			self.showInfos()
		self.keyLocked = False

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		self['name'].setText(title)
		self['handlung'].setText("%s: %s\nRuntime: %s" % (_("Sort order"),self.sorttext,runtime))
		CoverHelper(self['coverArt']).getCover(pic)

	def keySort(self):
		if self.keyLocked:
			return
		if re.match(".*?Search", self.Name):
			rangelist = [['Newest', 'newest'], ['Most Relevant','mostrelevant'], ['Featured','featured'], ['Most Popular','most-popular'], ['Top Rated','top-rated'], ['Longest','longest']]
		else:
			rangelist = [['Newest', 'newest'], ['Featured','featured'], ['Most Popular','most-popular'], ['Top Rated','top-rated'], ['Longest','longest']]
		self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keySortAction(self, result):
		if result:
			self.sort = result[1]
			self.sorttext = result[0]
			self.loadPage()

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.keyLocked = True
		twAgentGetPage(Link, agent=agent, cookieJar=cookies).addCallback(self.getVideoUrl).addErrback(self.dataError)

	def getVideoUrl(self, data):
		videoUrl = re.findall('\d+p"."(.*?)"', data, re.S)
		if videoUrl:
			self.keyLocked = False
			url = self.baseurl + videoUrl[-1].replace('\/','/')
			tw_agent_hlp = TwAgentHelper(cookieJar=cookies)
			tw_agent_hlp.getRedirectedUrl(url).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, url):
			Title = self['liste'].getCurrent()[0][0]
			mp_globals.player_agent = agent
			self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='pinflix')