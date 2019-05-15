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

myagent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
BASE_NAME = "DDFNetwork.com"
default_cover = "file://%s/ddfnetwork.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class ddfnetworkGenreScreen(MPScreen):

	def __init__(self, session, mode='Genres'):
		self.mode = mode

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

		self['title'] = Label(BASE_NAME)
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
		url = "https://ddfnetwork.com/videos/search/latest/ever/allsite/-/1"
		getPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		if self.mode == "Genres":
			parse = re.search('filterSelect" multiple name="tags">(.*?)</select>', data, re.S)
		else:
			parse = re.search('filterWebsiteSelect" multiple name="tags">(.*?)</select>', data, re.S)
		Cats = re.findall('data-mode="(.*?)">(.*?)</option>', parse.group(1), re.S)
		if Cats:
			for (Url, Title) in Cats:
				if self.mode == "Genres":
					Url = "https://ddfnetwork.com/videos/search/latest/ever/allsite/%s/" % Url
					Title = Title.title()
				else:
					Url = "https://ddfnetwork.com/videos/search/latest/ever/%s/-/" % Url
				self.genreliste.append((decodeHtml(Title), Url, default_cover))
			self.genreliste.sort(key=lambda t : t[0].lower())
		if self.mode == "Genres":
			self.genreliste.insert(0, ("Sites", 'https://ddfnetwork.com/sites/oursites', default_cover))
			self.genreliste.insert(0, ("Pornstars", 'https://ddfnetwork.com/pornstars/search/popular/females/-/-/', default_cover))
			self.genreliste.insert(0, ("Most Viewed", 'https://ddfnetwork.com/videos/search/viewed/ever/allsite/-/', default_cover))
			self.genreliste.insert(0, ("Most Popular", 'https://ddfnetwork.com/videos/search/rated/ever/allsite/-/', default_cover))
			self.genreliste.insert(0, ("Trending", 'https://ddfnetwork.com/videos/trending/', default_cover))
			self.genreliste.insert(0, ("Featured", 'https://ddfnetwork.com/videos/featured/', default_cover))
			self.genreliste.insert(0, ("Latest", 'https://ddfnetwork.com/videos/search/latest/ever/allsite/-/', default_cover))
			self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		if not config_mp.mediaportal.premiumize_use.value:
			message = self.session.open(MessageBoxExt, _("%s only works with enabled MP premiumize.me option (MP Setup)!" % BASE_NAME), MessageBoxExt.TYPE_INFO, timeout=10)
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		elif Name == "Sites":
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(ddfnetworkGenreScreen, Name)
		elif Name == "Pornstars":
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(ddfnetworkPornstarsScreen, Link, Name)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(ddfnetworkFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = callback
			Name = "--- Search ---"
			Link = urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(ddfnetworkFilmScreen, Link, Name)

class ddfnetworkPornstarsScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label(BASE_NAME)
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
		url = "%s%s" % (self.Link, str(self.page))
		getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pagination(.*?)</ul>', '.*(?:\/|\">)(\d+)(?:\"|</a)')
		Pornstars = re.findall('class="card.*?itemprop="name"\scontent="(.*?)".*?href="(.*?)".*?data-src="(.*?)"', data, re.S)
		if Pornstars:
			for (Title, Url, Image) in Pornstars:
				Url = "https://ddfnetwork.com" + Url
				if Image.startswith('//'):
					Image = 'https:' + Image
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No pornstars found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, int(self.lastpage), mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(ddfnetworkFilmScreen, Link, Name)

class ddfnetworkFilmScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label(BASE_NAME)
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
			url = "https://ddfnetwork.com/videos/freeword/%s/%s" % (self.Link, str(self.page))
		else:
			url = "%s%s/" % (self.Link, str(self.page))
		getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pagination(.*?)</ul>', '.*(?:\/|\">)(\d+)(?:\"|</a)')
		Movies = re.findall('class="card\s.*?href="(.*?)"\stitle="(.*?)".*?data-src="(.*?)".*?"card-subtitle.*?">(.*?)</h6>.*?icon-eye">.*?card-text">(.*?)</.*?icon-video">.*?card-text">(.*?)</p.*?datetime="(.*?)"', data, re.S)
		if Movies:
			for (Url, Title, Image, Pornstars, Views, Runtime, Date) in Movies:
				if Image.startswith('//'):
					Image = "https:" + Image
				Url = "https://ddfnetwork.com" + Url
				Pornstars = stripAllTags(Pornstars)
				Title = Pornstars + " - " + Title
				self.filmliste.append((decodeHtml(Title), Url, Image, Date, Runtime, Views))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None, ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, int(self.lastpage), mode=0)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		date = self['liste'].getCurrent()[0][3]
		runtime = self['liste'].getCurrent()[0][4]
		views = self['liste'].getCurrent()[0][5]
		self['handlung'].setText("Runtime: "+runtime+"\nDate: "+date+'\nViews: '+views)
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		get_stream_link(self.session).check_link(Link, self.play)

	def play(self, url):
		title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(title, url.replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B'))], showPlaylist=False, ltype='ddfnetwork')