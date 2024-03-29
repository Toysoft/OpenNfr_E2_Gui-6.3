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

json_headers = {
	'Accept':'application/json, text/plain, */*',
	'Accept-Encoding':'deflate',
	'Accept-Language':'de,en-US;q=0.7,en;q=0.3',
	'Content-Type':'application/json;charset=utf-8'
	}
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
default_cover = "file://%s/hotscope.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

BASE_URL = 'https://api.hotscope.tv/'

class hotscopeGenreScreen(MPScreen):

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

		self['title'] = Label("Hotscope.tv")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "https://hotscope.tv/categories"
		twAgentGetPage(url, agent=agent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('<a.*?href="/category/(.*?)".*?data-src="(.*?)"', data, re.S)
		if Cats:
			for (Url, Image) in Cats:
				Title = Url.title()
				Url = BASE_URL + "videos/category?category=" + Url + "&page="
				self.genreliste.append((Title, Url, Image))
			self.genreliste.sort()
			self.genreliste.insert(0, ("Porn", BASE_URL + "videos/group?group=other&page=", default_cover))
			self.genreliste.insert(0, ("Periscope", BASE_URL + "videos/group?group=periscope&page=", default_cover))
			self.genreliste.insert(0, ("Most Viewed", BASE_URL + "videos/sortBy?sort=-views&page=", default_cover))
			self.genreliste.insert(0, ("Most Recent", BASE_URL + "videos/sortBy?sort=-date&page=", default_cover))
			self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.ml.moveToIndex(0)
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
			self.session.open(hotscopeFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = urllib.quote(self.suchString).replace(' ', '%20')
			self.session.open(hotscopeFilmScreen, Link, Name)

class hotscopeFilmScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label("Hotscope.tv")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 999

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if re.match(".*Search", self.Name):
			url = BASE_URL + "videos/search?search=%s&page=%s" % (self.Link, str(self.page))
		else:
			url = self.Link + str(self.page)
		twAgentGetPage(url, agent=agent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		json_data = json.loads(data)
		self['page'].setText(str(self.page))
		if json_data:
			for item in json_data:
				title = str(item['title'])
				image = str(item['image'])
				id = str(item['id'])
				group = str(item['group'])
				self.filmliste.append((decodeHtml(title), group, id, image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][3]
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		group = self['liste'].getCurrent()[0][1]
		id = self['liste'].getCurrent()[0][2]
		if group and id:
			if group == "other":
				url = "https://hotscope.tv/snapchat/%s" % id
			else:
				url = "https://hotscope.tv/%s/%s" % (group, id)
			twAgentGetPage(url, agent=agent).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		video = re.findall('<video preload.*?src="(.*?)"', data, re.S)
		if video:
			url = video[-1]
			Title = self['liste'].getCurrent()[0][0]
			self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='hotscope')
		else:
			embedurl = re.findall('"embedURL":"https://\w+.pornhub.com/embed/(.*?)",', data.replace('\u002F','/'), re.S)
			if embedurl:
				url = "https://www.pornhub.com/view_video.php?viewkey=" + embedurl[0]
				twAgentGetPage(url, agent=agent).addCallback(self.getVideoPage2).addErrback(self.dataError)

	def getVideoPage2(self, data):
		match = re.findall('quality":"720","videoUrl"."(.*?)"', data, re.S)
		if not match:
			match = re.findall('quality":"480","videoUrl"."(.*?)"', data, re.S)
		if not match:
			match = re.findall('quality":"240","videoUrl"."(.*?)"', data, re.S)
		fetchurl = urllib2.unquote(match[0]).replace('\/','/')

		# retry till we get a good working cdn streamurl
		if config_mp.mediaportal.pornhub_cdnfix.value:
			if re.match('.*?bv.phncdn.com', fetchurl, re.S):
				self.count += 1
				if self.count < 20:
					self.keyOK()
					printl('CDN retry: '+str(self.count),self,'A')
					return

		Title = self['liste'].getCurrent()[0][0]
		mp_globals.player_agent = agent
		if "&hash=" in fetchurl:
			url = fetchurl.split('&hash=')
			url = url[0] + "&hash=" + url[1].replace('/','%252F').replace('=','%253D').replace('+','%252B')
		else:
			url = fetchurl
		self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='hotscope')