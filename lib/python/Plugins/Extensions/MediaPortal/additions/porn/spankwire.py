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
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt

agent='Mozilla/5.0 (Windows NT 6.1; rv:44.0) Gecko/20100101 Firefox/44.0'
headers = {
	'Accept-Language':'de,en-US;q=0.7,en;q=0.3',
	'X-Requested-With':'XMLHttpRequest',
	}
default_cover = "file://%s/spankwire.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class spankwireGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"yellow" : self.keyScope
		}, -1)

		self.scope = 0
		self.scopeText = ['Straight', 'Shemale', 'Gay']
		self.scopeval = ['Straight', 'Tranny', 'Gay']

		self['title'] = Label("Spankwire.com")
		self['ContentTitle'] = Label("Genre:")
		self['F3'] = Label(self.scopeText[self.scope])

		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.dupe = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.page = 1
		self.lastpage = 16

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self['F3'].setText(self.scopeText[self.scope])
		self['name'].setText(_('Please wait...'))
		url = "https://www.spankwire.com/api/categories/list.json?page=%s&segmentId=%s&sort=recent&limit=100" % (str(self.page), str(self.scope))
		twAgentGetPage(url, agent=agent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		json_data = json.loads(data)
		for item in json_data["items"]:
			count = int(item["videosNumber"])
			title = str(item["name"])
			id = str(item["id"])
			image = str(item["image"])
			if not title in self.dupe:
				if count > 250:
					self.genreliste.append((title, id, "recent", image))
					self.dupe.append((title))
		if self.page == self.lastpage:
			# remove duplicates
			self.genreliste = list(set(self.genreliste))
			self.genreliste.sort()
			self.genreliste.insert(0, ("Longest", "", "duration", default_cover))
			self.genreliste.insert(0, ("Most Commented", "", "comments", default_cover))
			self.genreliste.insert(0, ("Most Viewed", "", "views", default_cover))
			self.genreliste.insert(0, ("Trending", "", "trending", default_cover))
			self.genreliste.insert(0, ("Top Rated", "", "rating", default_cover))
			self.genreliste.insert(0, ("Most Recent", "", "recent", default_cover))
			self.genreliste.insert(0, ("--- Search ---", "", "callSuchen", default_cover))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.ml.moveToIndex(0)
			self.keyLocked = False
			self['name'].setText('')
			self.showInfos()
		else:
			self.page += 1
			self.layoutFinished()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][3]
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen(suggest_func=self.getSuggestions)
		else:
			Link = self['liste'].getCurrent()[0][1]
			Sort = self['liste'].getCurrent()[0][2]
			self.session.open(spankwireFilmScreen, Link, Name, Sort, Scope=self.scopeval[self.scope])

	def keyScope(self):
		if self.keyLocked:
			return
		self.genreliste = []
		self.dupe = []
		if self.scope == 0:
			self.scope = 1
		elif self.scope == 1:
			self.scope = 2
		else:
			self.scope = 0
		self.page = 1
		self.layoutFinished()

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = self['liste'].getCurrent()[0][0]
			self.suchString = callback
			Link = '%s' % urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(spankwireFilmScreen, Link, Name, "", Scope=self.scopeval[self.scope])

	def getSuggestions(self, text, max_res):
		url = "http://www.pornmd.com/autosuggest?key=%s" % urllib.quote_plus(text)
		d = twAgentGetPage(url, agent=agent, headers=headers, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, err=True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and type(suggestions) in (str, buffer):
			suggestions = json.loads(suggestions)
			for item in suggestions:
				li = item
				list.append(str(li))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

class spankwireFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, Sort, Scope='Straight'):
		self.Link = Link
		self.Name = Name
		self.Sort = Sort
		self.Scope = Scope
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

		self['title'] = Label("Spankwire.com")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))

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
			url = "https://www.spankwire.com/api/video/search.json?limit=50&page=%s&query=%s" % (str(self.page), self.Link)
		else:
			url = "https://www.spankwire.com/api/video/list.json?segment=%s&limit=50&page=%s&sortby=%s&sort=Relevance&period=All_Time" % (self.Scope, str(self.page), self.Sort)
			if self.Link:
				url = url + "&category=%s" % self.Link
		twAgentGetPage(url, agent=agent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		json_data = json.loads(data)
		if json_data.has_key('pages'):
			self.lastpage = int(json_data["pages"])
		if self.lastpage > 1:
			self['Page'].setText(_("Page:"))
			self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		for node in json_data["items"]:
			Views = str(node["viewed"]).replace(',','')
			Title = str(node["title"])
			Seconds = int(node["duration"])
			m, s = divmod(Seconds, 60)
			Runtime = "%02d:%02d" % (m, s)
			Url = str(node["videoId"])
			Image = str(node["poster2x"])
			if Image.startswith('//'):
				Image = 'http:' + Image
			self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), None, None, '', ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		self['name'].setText(title)
		self['handlung'].setText("Runtime: %s\nViews: %s" % (runtime, views))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			self.keyLocked = True
			url = "https://www.spankwire.com/api/video/%s.json" % Link
			twAgentGetPage(url, agent=agent).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		json_data = json.loads(data)
		url = None
		if json_data["videos"].has_key('quality_720p'):
			url = str(json_data["videos"]["quality_720p"])
		elif json_data["videos"].has_key('quality_480p'):
			url = str(json_data["videos"]["quality_480p"])
		elif json_data["videos"].has_key('quality_240p'):
			url = str(json_data["videos"]["quality_240p"])
		elif json_data["videos"].has_key('quality_180p'):
			url = str(json_data["videos"]["quality_180p"])
		self.keyLocked = False
		Title = self['liste'].getCurrent()[0][0]
		if url:
			self.session.open(SimplePlayer, [(Title, url.replace('%2F','%252F').replace('%3D','%253D').replace('%2B','%252B'))], showPlaylist=False, ltype='spankwire')