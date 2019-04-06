# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

default_cover = "file://%s/ivhunter.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

try:
	from Plugins.Extensions.MediaPortal.resources import cfscrape
except:
	cfscrapeModule = False
else:
	cfscrapeModule = True

try:
	import requests
except:
	requestsModule = False
else:
	requestsModule = True

import urlparse
import thread

iv_cookies = CookieJar()
iv_ck = {}
iv_agent = ''

BASE_URL = "http://javdos.com"

class ivhunterGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel
		}, -1)

		self['title'] = Label("IVHUNTER")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		thread.start_new_thread(self.get_tokens,("GetTokens",))

	def get_tokens(self, threadName):
		if requestsModule and cfscrapeModule:
			printl("Calling thread: %s" % threadName,self,'A')
			global iv_ck
			global iv_agent
			if iv_ck == {} or iv_agent == '':
				iv_ck, iv_agent = cfscrape.get_tokens(BASE_URL)
				requests.cookies.cookiejar_from_dict(iv_ck, cookiejar=iv_cookies)
			else:
				try:
					s = requests.session()
					url = urlparse.urlparse(BASE_URL)
					headers = {'user-agent': iv_agent}
					page = s.get(url.geturl(), cookies=iv_cookies, headers=headers, timeout=15, allow_redirects=False)
					if page.status_code == 503 and page.headers.get("Server", "").startswith("cloudflare") and b"jschl_vc" in page.content and b"jschl_answer" in page.content:
						iv_ck, iv_agent = cfscrape.get_tokens(BASE_URL)
						requests.cookies.cookiejar_from_dict(iv_ck, cookiejar=iv_cookies)
				except:
					pass
			self.keyLocked = False
			reactor.callFromThread(self.getGenres)
		else:
			reactor.callFromThread(self.iv_error)

	def iv_error(self):
		message = self.session.open(MessageBoxExt, _("Mandatory depends python-requests and/or python-pyexecjs and nodejs are missing!"), MessageBoxExt.TYPE_ERROR)
		self.keyCancel()

	def getGenres(self):
		url = BASE_URL
		twAgentGetPage(url, agent=iv_agent, cookieJar=iv_cookies).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('href=[\'|\"].*?(\/studios\/.*?)[\'|\"].*?>(.*?)</a', data, re.S)
		if Cats:
			dup_items = set()
			for (Url, Title) in Cats:
				if not Url.startswith('http'):
					Url = BASE_URL + Url
				if Url.lower() not in dup_items:
					if Title != "Studios":
						self.genreliste.append((Title, Url.lower(), None))
						dup_items.add(Url.lower())
			self.genreliste = list(set(self.genreliste))
			self.genreliste.append(("Junior Idol", "%s/junior-idol/" % BASE_URL, None))
			self.genreliste.sort(key=lambda t : t[0].lower())
		self.genreliste.insert(0, ("HD", "%s/hd-video/" % BASE_URL, None))
		self.genreliste.insert(0, ("Newest", "%s/" % BASE_URL, None))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = urllib.quote(callback).replace(' ', '+')
			Name = "--- Search ---"
			Link = '%s' % (self.suchString)
			self.session.open(ivhunterFilmScreen, Link, Name)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(ivhunterFilmScreen, Link, Name)

class ivhunterFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions2", "MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"upUp" : self.key_repeatedUp,
			"rightUp" : self.key_repeatedUp,
			"leftUp" : self.key_repeatedUp,
			"downUp" : self.key_repeatedUp,
			"upRepeated" : self.keyUpRepeated,
			"downRepeated" : self.keyDownRepeated,
			"rightRepeated" : self.keyRightRepeated,
			"leftRepeated" : self.keyLeftRepeated,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("IVHUNTER")
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
			if self.page > 1:
				url = "%s/page/%s/?s=%s" % (BASE_URL, str(self.page), self.Link)
			else:
				url = "%s/?s=%s" % (BASE_URL, self.Link)
		else:
			if self.page > 1:
				url = self.Link + "page/" + str(self.page)
			else:
				url = self.Link
		twAgentGetPage(url, agent=iv_agent, cookieJar=iv_cookies).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class=\'wp-pagenavi\'>(.*?)</div>', '.*\/page\/(\d+)')
		Movies = re.findall('id="post-\d+".*?clip-link.*?title="(.*?)"\shref="(.*?)".*?img\ssrc="(.*?)"', data, re.S)
		if Movies:
			for (Title, Url, Image) in Movies:
				if not Image and "/category/" in Url:
					pass
				else:
					if not Image.startswith('http'):
						Image = BASE_URL + Image
					Image = Image.replace('https://pics.dmm.co.jp','http://pics.dmm.co.jp').replace('https://pics.dmm.com','http://pics.dmm.co.jp')
					if not Url.startswith('http'):
						Url = BASE_URL + Url
					self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.loadPicQueued()

	def showInfos(self):
		CoverHelper(self['coverArt']).getCover(default_cover)
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)

	def loadPic(self):
		if self.picQ.empty():
			self.eventP.clear()
			return
		while not self.picQ.empty():
			self.picQ.get_nowait()
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamPic = self['liste'].getCurrent()[0][2]
		self.showInfos()
		self.updateP = 1
		CoverHelper(self['coverArt'], self.ShowCoverFileExit).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		self['name'].setText(_('Please wait...'))
		self.keyLocked = True
		url = self['liste'].getCurrent()[0][1]
		if url:
			twAgentGetPage(url, agent=iv_agent, cookieJar=iv_cookies).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		streams = re.findall('<iframe\ssrc="((?:http[s]?|)//javdos.com/embed.*?)"', data, re.S)
		if streams:
			url = streams[0]
			if url.startswith('//'):
				url = 'http:' + url
			twAgentGetPage(url, agent=iv_agent, cookieJar=iv_cookies).addCallback(self.loadStreamData).addErrback(self.dataError)

	def loadStreamData(self, data):
		js = re.findall('<script type="text/javascript">(.*?)</script>', data, re.S)
		if js:
			for item in js:
				if "monday" in item:
					js = item
					break
			monday = re.findall('clientSide.init\((monday.*?\))\);', data, re.S)
			if monday:
				js = js + "vidurl = " + monday[0] + ";return vidurl;"
				try:
					import execjs
					node = execjs.get("Node")
					url = str(node.exec_(js))
					get_stream_link(self.session).check_link(url, self.got_link)
					self.keyLocked = False
				except:
					self.session.open(MessageBoxExt, _("This plugin requires packages python-pyexecjs and nodejs."), MessageBoxExt.TYPE_INFO)
			else:
				message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)
				self.keyLocked = False
		else:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)
			self.keyLocked = False

	def got_link(self, stream_url):
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)
		mp_globals.player_agent = iv_agent
		self.session.open(SimplePlayer, [(title, stream_url)], showPlaylist=False, ltype='ivhunter')