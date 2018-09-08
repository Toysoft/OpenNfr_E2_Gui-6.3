# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.DelayedFunction import DelayedFunction

myagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

mdh_ck = {}
mdh_ck2 = {}
mdh_cookies = CookieJar()

default_cover = "file://%s/mydirtyhobby.png" % (config.mediaportal.iconcachepath.value + "logos")

class MDHGenreNewScreen(MPScreen):

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

		self['title'] = Label("Stream-MDH")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self['name'].setText(_("Please wait..."))
		url = "https://www.stream-mydirtyhobby.co"
		getPage(url, agent=myagent, cookies=mdh_ck2, headers={'Referer':'https://www.stream-mydirtyhobby.co/'}, timeout=30).addCallback(self.checkData).addErrback(self.dataError)

	def checkData(self, data):
		if "XMLHttpRequest" in data:
			parse = re.findall('GET","(.*?)".*?"(.*?)"', data, re.S)
			url = "https://www.stream-mydirtyhobby.co" + parse[0][0] + str(random.randint(1400,1800)) + parse[0][1]
			DelayedFunction(4000, self.getJs, url)
		elif 'class="g-recaptcha"' in data:
			self['name'].setText('')
			self.session.open(MessageBoxExt, _("Google reCAPTCHA detected, please verify your current IP by\naccessing the website 'https://www.stream-mydirtyhobby.co' with your browser."), MessageBoxExt.TYPE_INFO)
		else:
			self.genreData(data)

	def getJs(self, url):
		getPage(url, agent=myagent, cookies=mdh_ck2, headers={'Referer':'https://www.stream-mydirtyhobby.co'}, timeout=30).addCallback(self.getJs2).addErrback(self.dataError)

	def getJs2(self, data):
		try:
			import execjs
			node = execjs.get("Node")
		except:
			printl('nodejs not found',self,'E')
			self.session.open(MessageBoxExt, _("This plugin requires packages python-pyexecjs and nodejs."), MessageBoxExt.TYPE_INFO)
			return
		js = re.search('(.*?)if\(\$\(window', data, re.S).group(1)
		js = js + "function go(){ cookie = toHex(BFCrypt.decrypt(c, 2, a, b)) };"
		js = js + 'go(); return cookie;'
		result = node.exec_(js)
		printl('BLAZINGFAST-WEB-PROTECT: '+result,self,'A')
		mdh_ck2.update({'BLAZINGFAST-WEB-PROTECT':str(result)})
		url = "https://www.stream-mydirtyhobby.co/"
		getPage(url, agent=myagent, cookies=mdh_cookies2, headers={'Referer':'https://www.stream-mydirtyhobby.co/'}, timeout=30).addCallback(self.genreData).addErrback(self.genreData)

	def genreData(self, data=None):
		self['name'].setText('')
		self.genreliste.insert(0, ("Stream-MDH (Old)", None))
		self.genreliste.insert(0, ("Being Watched", "https://www.stream-mydirtyhobby.co/videos?t=a&o=bw&page="))
		self.genreliste.insert(0, ("Most Viewed", "https://www.stream-mydirtyhobby.co/videos?t=a&o=mv&page="))
		self.genreliste.insert(0, ("Newest", "https://www.stream-mydirtyhobby.co/videos?t=a&o=mr&page="))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.suchen()
		elif Name == "Stream-MDH (Old)":
			self.session.open(MDHGenreScreen)
		else:
			self.session.open(MDHFilmNewScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = self.suchString.replace(' ', '+')
			self.session.open(MDHFilmNewScreen, Link, Name)

class MDHGenreScreen(MPScreen):

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

		self['title'] = Label("Stream-MDH (Old)")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self['name'].setText(_("Please wait..."))
		url = "http://old.stream-mdh.se"
		twAgentGetPage(url, agent=myagent, cookieJar=mdh_cookies, headers={'Referer':'http://old.stream-mdh.se/'}, timeout=30).addCallback(self.checkData).addErrback(self.dataError)

	def checkData(self, data):
		if "XMLHttpRequest" in data:
			parse = re.findall('GET","(.*?)".*?"(.*?)"', data, re.S)
			url = "http://old.stream-mdh.se" + parse[0][0] + str(random.randint(1400,1800)) + parse[0][1]
			DelayedFunction(4000, self.getJs, url)
		elif 'class="g-recaptcha"' in data:
			self['name'].setText('')
			self.session.open(MessageBoxExt, _("Google reCAPTCHA detected, please verify your current IP by\naccessing the website 'http://old.stream-mdh.se' with your browser."), MessageBoxExt.TYPE_INFO)
		else:
			self.genreData(data)

	def getJs(self, url):
		twAgentGetPage(url, agent=myagent, cookieJar=mdh_cookies, headers={'Referer':'http://old.stream-mdh.se'}, timeout=30).addCallback(self.getJs2).addErrback(self.dataError)

	def getJs2(self, data):
		try:
			import execjs
			node = execjs.get("Node")
		except:
			printl('nodejs not found',self,'E')
			self.session.open(MessageBoxExt, _("This plugin requires packages python-pyexecjs and nodejs."), MessageBoxExt.TYPE_INFO)
			return
		js = re.search('(.*?)if\(\$\(window', data, re.S).group(1)
		js = js + "function go(){ cookie = toHex(BFCrypt.decrypt(c, 2, a, b)) };"
		js = js + 'go(); return cookie;'
		result = node.exec_(js)
		printl('BLAZINGFAST-WEB-PROTECT: '+result,self,'A')
		import requests
		mdh_ck = requests.utils.dict_from_cookiejar(mdh_cookies)
		mdh_ck.update({'BLAZINGFAST-WEB-PROTECT':str(result)})
		requests.cookies.cookiejar_from_dict(mdh_ck, cookiejar=mdh_cookies)
		url = "http://old.stream-mdh.se/empty"
		twAgentGetPage(url, agent=myagent, cookieJar=mdh_cookies, headers={'Referer':'http://old.stream-mdh.se/'}, timeout=30).addCallback(self.genreData).addErrback(self.genreData)

	def genreData(self, data=None):
		self['name'].setText('')
		self.genreliste.insert(0, ("Most Commented", "http://old.stream-mdh.se/channel/video/general?page=%s&filter=comments"))
		self.genreliste.insert(0, ("Most Viewed", "http://old.stream-mdh.se/channel/video/general?page=%s&filter=views"))
		self.genreliste.insert(0, ("Most Popular", "http://old.stream-mdh.se/channel/video/general?page=%s&filter=likes"))
		self.genreliste.insert(0, ("Newest", "http://old.stream-mdh.se/channel/video/general?page=%s&filter=date"))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.suchen()
		else:
			self.session.open(MDHFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = self.suchString.replace(' ', '%20')
			self.session.open(MDHFilmScreen, Link, Name)

class MDHFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"5" : self.keyShowThumb,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber,
			"yellow" : self.keyRelated
		}, -1)

		self['title'] = Label("Stream-MDH (Old)")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		self['F3'] = Label(_("Related"))

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
			url = "http://old.stream-mdh.se/search/%s?page=%s" % (self.Link, str(self.page))
		else:
			url = self.Link % str(self.page)
		twAgentGetPage(url, agent=myagent, cookieJar=mdh_cookies, headers={'Referer':'http://old.stream-mdh.se/'}, timeout=30).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pager">(.*?)</div>', '.*[>|=](\d+)[<|&|"]')
		parse = re.search("(.*?)id='sidebar_categories'>", data, re.S)
		Movies = re.findall("class='mediathumb'.*?ref='(.*?)'.*?class='mediabg'.*?url\((.*?)\)'>(.*?)</span>.*?'mediadate'>(.*?)</span>.*?'mediaviews'>(\d+,{0,1}\d+).*?</span>", parse.group(1), re.S)
		if Movies:
			for (Url, Image, Title, Added, Views) in Movies:
				self.filmliste.append((decodeHtml(Title), Url, Image, Views, Added))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None, '', ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		import requests
		mdh_ck = requests.utils.dict_from_cookiejar(mdh_cookies)
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1, agent=myagent, cookies=mdh_ck)
		self.showInfos()
		self.keyLocked = False

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		views = self['liste'].getCurrent()[0][3].replace(',','')
		added = self['liste'].getCurrent()[0][4]
		self['name'].setText(title)
		self['handlung'].setText("Views: %s\nAdded: %s" % (views, added))
		CoverHelper(self['coverArt']).getCover(pic, agent=myagent, cookieJar=mdh_cookies)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.keyLocked = True
		twAgentGetPage(Link, agent=myagent, cookieJar=mdh_cookies, headers={'Referer':'http://old.stream-mdh.se/'}, timeout=30).addCallback(self.getVideoUrl).addErrback(self.dataError)

	def keyRelated(self):
		Link = self['liste'].getCurrent()[0][0]
		if " - " in Link:
			Link = Link.split(' - ')[0]
			Name = "--- Search ---"
			self.session.open(MDHFilmScreen, Link, Name)

	def getVideoUrl(self, data):
		url = re.findall("iframe\ssrc='(.*?)'", data, re.S|re.I)
		if url:
			twAgentGetPage(url[0], agent=myagent, cookieJar=mdh_cookies, headers={'Referer':'http://old.stream-mdh.se/'}, timeout=30).addCallback(self.getVideoUrl2).addErrback(self.dataError)
		else:
			self.keyLocked = False

	def getVideoUrl2(self, data):
		url = re.findall('iframe\ssrc="(.*?)"', data, re.S|re.I)
		if url:
			get_stream_link(self.session).check_link(url[0], self.got_link)
			self.keyLocked = False

	def got_link(self, url):
		Title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='streammdh')

class MDHFilmNewScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"5" : self.keyShowThumb,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber,
			"yellow" : self.keyRelated
		}, -1)

		self['title'] = Label("Stream-MDH")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))
		self['F3'] = Label(_("Related"))

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
			url = "https://www.stream-mydirtyhobby.co/search/videos?search_query=%s&page=%s" % (self.Link, str(self.page))
		else:
			url = self.Link + str(self.page)
		getPage(url, agent=myagent, cookies=mdh_ck2, headers={'Referer':'https://www.stream-mydirtyhobby.co/'}).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pagination">(.*?)</div>', '.*[>|=](\d+)[<|&|"]>\d')
		Movies = re.findall('class="well well-sm.*?href="(.*?)".*?img\ssrc="(.*?)"\stitle="(.*?)"', data, re.S)
		if Movies:
			for (Url, Image, Title) in Movies:
				Url = "https://www.stream-mydirtyhobby.co" + Url
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1, agent=myagent)
		self.showInfos()
		self.keyLocked = False

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		self['name'].setText(title)
		CoverHelper(self['coverArt']).getCover(pic, agent=myagent)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.keyLocked = True
		getPage(Link, agent=myagent, cookies=mdh_ck2, headers={'Referer':'https://www.stream-mydirtyhobby.co/'}).addCallback(self.getVideoUrl).addErrback(self.dataError)

	def keyRelated(self):
		Link = self['liste'].getCurrent()[0][0]
		if " - " in Link:
			Link = Link.split(' - ')[0]
			Name = "--- Search ---"
			self.session.open(MDHFilmNewScreen, Link, Name)

	def getVideoUrl(self, data):
		url = re.findall('iframe\ssrc="(.*?)"', data, re.S|re.I)
		if url:
			get_stream_link(self.session).check_link(url[0], self.got_link)
			self.keyLocked = False

	def got_link(self, url):
		Title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='streammdh')