﻿# -*- coding: utf-8 -*-
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
BASE_NAME = "JulesJordan.com"
default_cover = "file://%s/julesjordan.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class julesjordanGenreScreen(MPScreen):

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
		url = "https://www.julesjordan.com/trial/category.php?id=3"
		getPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('<!--Title-->.*?href="(.*?).html">(.*?)</a>.*?src0_1x="(.*?)"', data, re.S)
		if Cats:
			for (Url, Title, Image) in Cats:
				Url = Url + "_%s_d.html"
				self.genreliste.append((decodeHtml(Title), Url, Image))
			self.genreliste.sort()
		self.genreliste.insert(0, ("Pornstars", 'https://www.julesjordan.com/trial/models/models_%s.html', default_cover))
		self.genreliste.insert(0, ("Most Popular", 'https://www.julesjordan.com/trial/categories/movies_%s_p.html', default_cover))
		self.genreliste.insert(0, ("Most Recent", 'https://www.julesjordan.com/trial/categories/movies_%s_d.html', default_cover))
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
		elif Name == "Pornstars":
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(julesjordanPornstarsScreen, Link, Name)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(julesjordanFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = callback
			Name = "--- Search ---"
			Link = urllib.quote(self.suchString).replace(' ', '%20')
			self.session.open(julesjordanFilmScreen, Link, Name)

class julesjordanPornstarsScreen(MPScreen, ThumbsHelper):

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
		url = self.Link % str(self.page)
		getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="page_totals">(.*?)</div>', '.*of\s(\d+)')
		Pornstars = re.findall('class="update_details">.*?\t<a\shref="(.*?)">(.*?)</a>.*?src0(?:_1x|)="(.*?)"', data, re.S)
		if Pornstars:
			for (Url, Title, Image) in Pornstars:
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No pornstars found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, self.page, int(self.lastpage), 1, 1, mode=1)
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
		self.session.open(julesjordanFilmScreen, Link, Name)

class julesjordanFilmScreen(MPScreen, ThumbsHelper):

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
			url = "https://www.julesjordan.com/trial/search.php?query=%s&page=%s" % (self.Link, str(self.page))
		else:
			if "%s" in self.Link:
				url = self.Link % str(self.page)
			else:
				url = self.Link
		getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="page_totals">(.*?)</div>', '.*of\s(\d+)')
		Movies = re.findall('Thumbnail -->.*?href="(.*?)".*?src0(?:_1x|)="(.*?)".*?">(.*?)</a>.*?(\d+&nbsp;min).*?<!-- Date -->(.*?\d{4})', data, re.S)
		if Movies:
			for (Url, Image, Title, Runtime, Date) in Movies:
				Date = Date.strip()
				Runtime = Runtime.replace('&nbsp;',' ')
				self.filmliste.append((decodeHtml(Title), Url, Image, Date, Runtime))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None, ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, int(self.lastpage), mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		date = self['liste'].getCurrent()[0][3]
		runtime = self['liste'].getCurrent()[0][4]
		self['handlung'].setText("Date: "+date+"\nRuntime: "+runtime)
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		get_stream_link(self.session).check_link(Link, self.play)

	def play(self, url):
		title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(title, url.replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B'))], showPlaylist=False, ltype='julesjordan')