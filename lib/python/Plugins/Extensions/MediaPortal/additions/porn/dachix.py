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

default_cover = "file://%s/dachix.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class dachixGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		global default_cover
		if self.mode == "dachix":
			self.portal = "DaChix.com"
			self.baseurl = "http://www.dachix.com"
			default_cover = "file://%s/dachix.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "deviantclip":
			self.portal = "DeviantClip.com"
			self.baseurl = "http://www.deviantclip.com"
			default_cover = "file://%s/deviantclip.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label(_("Please wait..."))

		self.keyLocked = True
		self.suchString = ''

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.filmliste = []
		url = "%s/categories" % self.baseurl
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('class="listing-categories">.*?<a\shref="(.*?)".*?class="title">(.*?)</b>.*?src="(.*?)"', data, re.S)
		if raw:
			for (Url, Title, Image) in raw:
				Url = self.baseurl + Url + "/videos"
				self.filmliste.append((decodeHtml(Title), Url, Image))
			self.filmliste.sort()
			self.filmliste.insert(0, ("Longest", "%s/videos?sort=longest" % self.baseurl, default_cover))
			self.filmliste.insert(0, ("Most Popular", "%s/videos?sort=popular" % self.baseurl, default_cover))
			self.filmliste.insert(0, ("Most Viewed", "%s/videos?sort=viewed" % self.baseurl, default_cover))
			self.filmliste.insert(0, ("Top Rated", "%s/videos?sort=rated" % self.baseurl, default_cover))
			self.filmliste.insert(0, ("Most Recent", "%s/videos" % self.baseurl, default_cover))
			self.filmliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
			self.ml.setList(map(self._defaultlistcenter, self.filmliste))
			self.keyLocked = False
			self.showInfos()
		self['name'].setText('')

	def showInfos(self):
		pic = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(pic)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = '%s' % urllib.quote(self.suchString).replace(' ', '-')
			self.session.open(dachixListScreen, Link, Name, self.portal, self.baseurl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(dachixListScreen, Link, Name, self.portal, self.baseurl)

class dachixListScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl

		global default_cover
		if self.portal == "DaChix.com":
			default_cover = "file://%s/dachix.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		elif self.portal == "DeviantClip.com":
			default_cover = "file://%s/deviantclip.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
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

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['name'] = Label(_("Please wait..."))
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))

		self.keyLocked = True
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.page = 1
		self.lastpage = 1
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "%s/s/%s?p=%s" % (self.baseurl, self.Link, str(self.page))
		elif re.match('.*?\?sort', self.Link, re.S):
			url = self.Link + "&p=" + str(self.page)
		else:
			url = self.Link + "?p=" + str(self.page)
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.getLastPage(data, 'class="main-sectionpaging">(.*?)</div>', '.*p=(\d+)"')
		raw = re.findall('class=\'thumb_container video\'\shref="(.*?)".*?src="(.*?)".*?alt="(.*?)".*?(?:duration"\scontent=".*?">|class=\'lenght_pics\'>)(.*?)\s-.*?class=\'blue\'>([0-9,]+|New\s)</span>', data, re.S)
		if raw:
			for (Url, Image, Title, Runtime, Views) in raw:
				if "New" in Views:
					Views = "-"
				else:
					Views = Views.replace(',','')
				Url = self.baseurl + Url
				self.filmliste.append((decodeHtml(Title).strip(), Url, Image, Runtime, Views))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		self['handlung'].setText("Runtime: %s\nViews: %s" % (runtime, views))
		self['name'].setText(title)
		pic = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			print Link
			getPage(Link).addCallback(self.getStreamData).addErrback(self.dataError)

	def getStreamData(self, data):
		title = self['liste'].getCurrent()[0][0]
		url = re.findall("<source src='(.*?)'", data, re.S)
		if url:
			self.session.open(SimplePlayer, [(title, url[0])], showPlaylist=False, ltype='dachix')