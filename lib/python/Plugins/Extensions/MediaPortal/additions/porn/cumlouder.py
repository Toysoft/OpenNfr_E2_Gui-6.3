# -*- coding: utf-8 -*-
##############################################################################################################
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
#  This applies to the source code as a whole as well as to parts of it, unless
#  explicitely stated otherwise.
#
#  If you want to use or modify the code or parts of it,
#  you have to keep OUR license and inform us about the modifications, but it may NOT be
#  commercially distributed other than under the conditions noted above.
#
#  As an exception regarding execution on hardware, you are permitted to execute this plugin on VU+ hardware
#  which is licensed by satco europe GmbH, if the VTi image is used on that hardware.
#
#  As an exception regarding modifcations, you are NOT permitted to remove
#  any copy protections implemented in this plugin or change them for means of disabling
#  or working around the copy protections, unless the change has been explicitly permitted
#  by the original authors. Also decompiling and modification of the closed source
#  parts is NOT permitted.
#
#  Advertising with this plugin is NOT allowed.
#  For other uses, permission from the authors is necessary.
#
##############################################################################################################

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt

myagent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
default_cover = "file://%s/cumlouder.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class cumlouderGenreScreen(MPScreen):

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

		self['title'] = Label("Cumlouder")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.count = 0

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		url = "https://www.cumlouder.com/categories/"
		twAgentGetPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)
		url = "https://www.cumlouder.com/categories/2/"
		twAgentGetPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('<a\stag-url=.*?href="(.*?)\?.*?"\stitle="(.*?)".*?thumb"\ssrc="(.*?)"', data, re.S)
		if Cats:
			for (Url, Title, Image) in Cats:
				Url = 'http://www.cumlouder.com%s' % Url
				self.genreliste.append((decodeHtml(Title).title(), Url, Image))
			self.count += 1
		if self.count == 2:
			self.genreliste.sort()
			self.genreliste.insert(0, (400 * "—", None, default_cover))
			self.genreliste.insert(0, ("Latest Channel Uploads", 'https://www.cumlouder.com/channels/videos/', default_cover))
			self.genreliste.insert(0, ("Channels", 'https://www.cumlouder.com/channels/', default_cover))
			self.genreliste.insert(0, ("Sites", 'https://www.cumlouder.com/sites/', default_cover))
			self.genreliste.insert(0, ("Series", 'https://www.cumlouder.com/', default_cover))
			self.genreliste.insert(0, ("Girls", 'https://www.cumlouder.com/girls/', default_cover))
			self.genreliste.insert(0, ("Newest", 'https://www.cumlouder.com/', default_cover))
			self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.ml.moveToIndex(0)
			self.keyLocked = False
			self['name'].setText('')
			self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.suchen()
		elif Name == "Series":
			self.session.open(cumlouderSeriesScreen, Link, Name)
		elif Name == "Sites":
			self.session.open(cumlouderSitesScreen, Link, Name)
		elif Name == "Channels":
			self.session.open(cumlouderChannelsScreen, Link, Name)
		elif Name == "Girls":
			self.session.open(cumlouderGirlsScreen, Link, Name)
		else:
			if Link:
				self.session.open(cumlouderFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = callback
			Name = "--- Search ---"
			Link = urllib.quote(self.suchString).replace(' ', '%20')
			self.session.open(cumlouderFilmScreen, Link, Name)

class cumlouderSeriesScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
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

		self['title'] = Label("Cumlouder")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)

		self.keyLocked = True

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		twAgentGetPage(self.Link, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		Series = re.findall('\(\d{3},\s\'home-categorias.*?href="(.*?)".*?img\ssrc="(.*?)".*?itemprop="name">(.*?)</h.*?<p>(.*?)\svideos', data, re.S)
		if Series:
			for (Url, Image, Title, Count) in Series:
				Title = Title.lower().title()
				if Image.startswith('//'):
					Image = 'http:' + Image
				self.filmliste.append((decodeHtml(Title), Url, Image, Count))
				self.filmliste.sort()
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No series found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		count = self['liste'].getCurrent()[0][3]
		self['handlung'].setText("Videos: "+count.strip())
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			self.session.open(cumlouderFilmScreen, Link, Name)

class cumlouderSitesScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
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

		self['title'] = Label("Cumlouder")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)

		self.keyLocked = True

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		twAgentGetPage(self.Link, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		Sites = re.findall('class="muestra-escena">.*?href="(.*?)"\stitle="(.*?)".*?thumb"\ssrc="(.*?)".*?img\ssrc="(.*?)"', data, re.S)
		if Sites:
			for (Url, Title, Image, Logo) in Sites:
				Url = "https://www.cumlouder.com" + Url
				if Image.startswith('//'):
					Image = 'http:' + Image
				self.filmliste.append((decodeHtml(Title), Url, Logo))
				self.filmliste.sort()
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No sites found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
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
		if Link:
			self.session.open(cumlouderFilmScreen, Link, Name)

class cumlouderChannelsScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("Cumlouder")
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
		url = "%s%s/" % (self.Link, str(self.page))
		twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="paginador"(.*?)</ul>')
		Girls = re.findall('channel-url=.*?href="(.*?)"\stitle="(.*?)".*?thumb"\ssrc="(.*?)".*?videos sprite"></span>(.*?)\sVideos', data, re.S)
		if Girls:
			for (Url, Title, Image, Count) in Girls:
				Url = "http://www.cumlouder.com" + Url
				if Image.startswith('//'):
					Image = 'http:' + Image
				self.filmliste.append((decodeHtml(Title), Url, Image, Count))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No channels found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		count = self['liste'].getCurrent()[0][3]
		self['handlung'].setText("Videos: "+count.strip())
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			self.session.open(cumlouderFilmScreen, Link, Name)

class cumlouderGirlsScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("Cumlouder")
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
		url = "%s%s/" % (self.Link, str(self.page))
		twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="paginador"(.*?)</ul>')
		Girls = re.findall('girl-url=.*?href="(.*?)"\stitle="(.*?)".*?thumb"\ssrc="(.*?)".*?videos sprite"></span>(.*?)\sVideos.*?puntaje sprite"></span>(.*?)</span', data, re.S)
		if Girls:
			for (Url, Title, Image, Count, Rating) in Girls:
				Url = "http://www.cumlouder.com" + Url
				if Image.startswith('//'):
					Image = 'http:' + Image
				self.filmliste.append((decodeHtml(Title), Url, Image, Count, Rating))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No girls found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		count = self['liste'].getCurrent()[0][3]
		rating = self['liste'].getCurrent()[0][4]
		self['handlung'].setText("Videos: "+count.strip()+'\nRating: '+rating.strip())
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(cumlouderFilmScreen, Link, Name)

class cumlouderFilmScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber,
			"blue" : self.keyFilter
		}, -1)

		self['title'] = Label("Cumlouder")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		if "/porn-videos/" in self.Link:
			self['F4'].setText(_("Filter"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		if "/porn-videos/" in self.Link:
			self.filter = '?show=cumlouder'
			self.filtername = 'Cumlouder'
		else:
			self.filter = ''
			self.filtername = ''

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "https://www.cumlouder.com/search/%s?q=%s" % (str(self.page), self.Link)
		else:
			if self.page == 1:
				url = self.Link
			else:
				url = "%s%s/" % (self.Link, str(self.page))
			if self.Name == "Newest":
				url = url + "?s=last"
			elif "/porn-videos/" in self.Link:
				url = url + self.filter
		twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="paginador"(.*?)</ul>')
		if 'class="box-link-productora">' in data:
			Movies = re.findall('class="muestra-escena"\shref="(.*?)"\stitle="(.*?)".*?class="thumb"\ssrc="(.*?)".*?vistas sprite"></span>(.*?)views.*?minutos sprite"></span>(.*?)(?:\sm|)</span.*?class="link-productora"\stitle="(.*?)"', data, re.S)
			if Movies:
				for (Url, Title, Image, Views, Runtime, Channel) in Movies:
					Url = "https://www.cumlouder.com" + Url
					if Image.startswith('//'):
						Image = 'http:' + Image
					self.filmliste.append((decodeHtml(Title), Url, Image, None, Runtime, Views, Channel))
		else:
			Movies = re.findall('class="muestra-escena"\shref="(.*?)"\stitle="(.*?)".*?class="thumb"\ssrc="(.*?)".*?vistas sprite"></span>(.*?)views.*?fecha sprite"></span>(.*?)</span.*?minutos sprite"></span>(.*?)(?:\sm|)</span', data, re.S)
			if Movies:
				for (Url, Title, Image, Views, Date, Runtime) in Movies:
					Url = "https://www.cumlouder.com" + Url
					if Image.startswith('//'):
						Image = 'http:' + Image
					self.filmliste.append((decodeHtml(Title), Url, Image, Date, Runtime, Views, None))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None, ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		date = self['liste'].getCurrent()[0][3]
		runtime = self['liste'].getCurrent()[0][4]
		views = self['liste'].getCurrent()[0][5]
		channel = self['liste'].getCurrent()[0][6]
		if self.filtername:
			filtername = "\n%s: %s" % (_("Filter"), self.filtername)
		else:
			filtername = ''
		if channel:
			self['handlung'].setText("Runtime: "+runtime.strip()+'\nViews: '+views.strip()+'\nChannel: '+channel+filtername)
		else:
			self['handlung'].setText("Runtime: "+runtime.strip()+'\nViews: '+views.strip()+'\nAdded: '+date.strip()+filtername)
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			twAgentGetPage(Link).addCallback(self.getVideoPage).addErrback(self.dataError)

	def keyFilter(self):
		if self.keyLocked:
			return
		if not "/porn-videos/" in self.Link:
			return
		rangelist = [ ['Cumlouder', '?show=cumlouder'], ['Channels', '?show=channels'], ['All', '?show=all'] ]
		self.session.openWithCallback(self.keyFilterAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keyFilterAction(self, result):
		if result:
			self.filter = result[1]
			self.filtername = result[0]
			self.loadPage()

	def getVideoPage(self, data):
		vid = re.findall('<source src="(.*?)"', data, re.S)
		if vid:
			url = vid[0].replace('&amp;','&')
			if url.startswith('//'):
				url = "http:" + url
			title = self['liste'].getCurrent()[0][0]
			self.session.open(SimplePlayer, [(title, url)], showPlaylist=False, ltype='cumlouder')