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

agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'

class vintagetubeGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		global default_cover
		if self.mode == "vintagetube":
			self.portal = "VintageTube.xxx"
			self.baseurl = "vintagetube.xxx"
			default_cover = "file://%s/vintagetube.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		if self.mode == "analdin":
			self.portal = "Analdin.com"
			self.baseurl = "analdin.com"
			default_cover = "file://%s/analdin.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
		if self.mode == "xozilla":
			self.portal = "Xozilla.com"
			self.baseurl = "xozilla.com"
			default_cover = "file://%s/xozilla.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

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
		self['name'].setText(_('Please wait...'))
		url = "https://api.%s/api/v1/categories?sort=most-videos&c=500&min_videos=25" % self.baseurl
		twAgentGetPage(url, agent=agent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		json_data = json.loads(data)
		for item in json_data["data"]:
			title = str(item["title"]).title()
			slug = str(item["slug"])
			image = str(item["thumb"])
			if self.mode == "vintagetube":
				url = "https://api.%s/api/v1/categories/%s?sort=latest&c=100&offset=" % (self.baseurl, slug)
			else:
				url = "https://www.%s/categories/%s/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=" % (self.baseurl, slug)
			if not re.search(r'[^A-Za-z0-9]', title):
				self.genreliste.append((title, url, image))
		self.genreliste.sort()

		self.genreliste.insert(0, ("Pornstars", "pornstars", default_cover))
		if self.mode == "vintagetube":
			self.genreliste.insert(0, ("Most Viewed", "https://api.%s/api/v1/videos?sort=most-viewed&tf=all-time&c=100&offset=" % self.baseurl, default_cover))
			self.genreliste.insert(0, ("Top Rated", "https://api.%s/api/v1/videos?sort=top-rated&tf=all-time&c=100&offset=" % self.baseurl, default_cover))
			self.genreliste.insert(0, ("Newest", "https://api.%s/api/v1/videos?sort=latest&tf=all-time&c=100&offset=" % self.baseurl, default_cover))
		else:
			self.genreliste.insert(0, ("Most Viewed", "https://www.%s/most-popular/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=video_viewed&from=" % self.baseurl, default_cover))
			self.genreliste.insert(0, ("Top Rated", "https://www.%s/top-rated/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=rating&from=" % self.baseurl, default_cover))
			self.genreliste.insert(0, ("Newest", "https://www.%s/latest-updates/?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=" % self.baseurl, default_cover))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.ml.moveToIndex(0)
		self['name'].setText('')
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image, default_cover=default_cover)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		elif Name == "Pornstars":
			self.session.open(vintagetubePornstarsScreen, self.portal, self.baseurl)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(vintagetubeFilmScreen, Link, Name, self.portal, self.baseurl)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = self['liste'].getCurrent()[0][0]
			self.suchString = callback
			Link = '%s' % urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(vintagetubeFilmScreen, Link, Name, self.portal, self.baseurl)

class vintagetubePornstarsScreen(MPScreen):

	def __init__(self, session, portal, baseurl):
		self.portal = portal
		self.baseurl = baseurl

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

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Model:")

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.genreliste = []
		url = "https://api.%s/api/v1/models?sort=most-videos&c=100&offset=%s" % (self.baseurl, str((self.page-1)*100))
		twAgentGetPage(url, agent=agent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		json_data = json.loads(data)
		if json_data.has_key('total'):
			self.lastpage = int(round((float(json_data["total"]) / 100) + 0.5))
		if self.lastpage > 1:
			self['Page'].setText(_("Page:"))
			self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		for node in json_data["data"]:
			Title = str(node["title"]).title()
			slug = str(node["slug"])
			Image = str(node["thumb"])
			if self.portal == "VintageTube.xxx":
				Url = "https://api.%s/api/v1/models/%s?c=100&offset=" % (self.baseurl, slug)
			else:
				Url = "https://www.%s/models/%s/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=" % (self.baseurl, slug)
			self.genreliste.append((decodeHtml(Title), Url, Image))
		self.ml.setList(map(self._defaultlistleft, self.genreliste))
		self.ml.moveToIndex(0)
		self['name'].setText('')
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image, default_cover=default_cover)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(vintagetubeFilmScreen, Link, Name, self.portal, self.baseurl)

class vintagetubeFilmScreen(MPScreen):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl
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

		self['title'] = Label(self.portal)
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
			self.url = "https://api.%s/api/v1/search?q=%s&c=100&offset=%s" % (self.baseurl, self.Link, str((self.page-1)*100))
		else:
			if self.Link.startswith('https://api'):
				self.url = self.Link + str((self.page-1)*100)
			else:
				self.url = self.Link + str(self.page)
		twAgentGetPage(self.url, agent=agent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		if self.url.startswith('https://api'):
			json_data = json.loads(data)
			if json_data.has_key('total'):
				self.lastpage = int(round((float(json_data["total"]) / 100) + 0.5))
			if self.lastpage > 1:
				self['Page'].setText(_("Page:"))
				self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
			if json_data.has_key('videos'):
				json_data = json_data["videos"]
			for node in json_data["data"]:
				Title = str(node["title"]).replace('.mp4','')
				m, s = divmod(node['duration'], 60)
				Runtime = "%02d:%02d" % (m, s)
				Url = str(node["link"])
				Image = str(node["thumb"])
				self.filmliste.append((decodeHtml(Title), Url, Image, Runtime))
		else:
			self.getLastPage(data, 'class="pagination"(.*?)$')
			videos = re.findall('video-link".*?href="(.*?)".*?thumb="(.*?)".*?class="duration">(.*?)</div>.*?class="title">(.*?)</strong>', data, re.S)
			if not videos:
				videos = re.findall('href="(.*?)"\sclass="item.*?\sthumb="(.*?)".*?class="duration">(.*?)</div>.*?class="title">(.*?)</strong>', data, re.S)
			if videos:
				for (url, image, runtime, title) in videos:
					if title.strip().endswith('...') or title == "":
						tmp1 = stripAllTags(title).split(' ')[0]
						tmp2 = url.rstrip('/').split('/')[-1].lower().replace(tmp1.lower(),'').replace('_',' ').replace('-',' ').strip()
						title = tmp1 + " " + tmp2
						title = ' '.join(s[:1].upper() + s[1:] for s in stripAllTags(title).split(' '))
						title = title.strip()
					self.filmliste.append((decodeHtml(title.strip()), url, image, runtime))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), None, None, '', ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		self['name'].setText(title)
		self['handlung'].setText("Runtime: %s" % runtime)
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		self['name'].setText(_('Please wait...'))
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			twAgentGetPage(Link, agent=agent).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		self['name'].setText('')
		videoPage = re.findall('video_(?:alt_|)url\d{0,1}:\s\'(.*?)\'', data, re.S)
		if not videoPage:
			videoPage = re.findall('"(?:mp4|hd\.mp4||fullhd\.mp4)":{"link":"(.*?)"', data, re.S)
		if videoPage:
			url = videoPage[-1]
			Title = self['liste'].getCurrent()[0][0]
			mp_globals.player_agent = agent
			self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='vintagetube')