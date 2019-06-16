# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt

try:
	if mp_globals.model in ["one"]:
		from Plugins.Extensions.MediaPortal.resources import cfscrape
	else:
		from Plugins.Extensions.MediaPortal.resources import cfscrape_old as cfscrape
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

pw_url = 'https://www4.primewire.ac'
pw_cookies = CookieJar()
pw_ck = {}
pw_agent = ''

default_cover = "file://%s/primewire.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class PrimeWireGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("PrimeWire")
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
		self['name'].setText(_("Please wait..."))

	def get_tokens(self, threadName):
		if requestsModule and cfscrapeModule:
			printl("Calling thread: %s" % threadName,self,'A')
			global pw_ck
			global pw_agent
			if pw_ck == {} or pw_agent == '':
				pw_ck, pw_agent = cfscrape.get_tokens(pw_url)
				requests.cookies.cookiejar_from_dict(pw_ck, cookiejar=pw_cookies)
			else:
				try:
					s = requests.session()
					url = urlparse.urlparse(pw_url)
					headers = {'user-agent': pw_agent}
					page = s.get(url.geturl(), cookies=pw_cookies, headers=headers, timeout=15, allow_redirects=False)
					if page.status_code == 503 and page.headers.get("Server", "").startswith("cloudflare") and b"jschl_vc" in page.content and b"jschl_answer" in page.content:
						pw_ck, pw_agent = cfscrape.get_tokens(pw_url)
						requests.cookies.cookiejar_from_dict(pw_ck, cookiejar=pw_cookies)
				except:
					pass
			reactor.callFromThread(self.getData)
		else:
			reactor.callFromThread(self.pw_error)

	def pw_error(self):
		message = self.session.open(MessageBoxExt, _("Mandatory depends python-requests and/or nodejs are missing!"), MessageBoxExt.TYPE_ERROR)
		self.keyCancel()

	def getData(self):
		self.keyLocked = True
		url = pw_url
		twAgentGetPage(url, agent=pw_agent, cookieJar=pw_cookies).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('class="opener-menu-genre">(.*)class="opener-menu-section', data, re.S)
		Cats = re.findall('<a\shref="(.*?)".*?>(.*?)</a>', parse.group(1), re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = pw_url + Url + "&page="
				self.genreliste.append((Title, Url))
		self.genreliste.sort()
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.genreliste.insert(1, ("Featured Movies", "%s/index.php?sort=featured&page=" % pw_url))
		self.genreliste.insert(2, ("Popular Movies", "%s/index.php?sort=views&page=" % pw_url))
		self.genreliste.insert(3, ("Top Rated Movies", "%s/index.php?sort=ratings&page=" % pw_url))
		self.genreliste.insert(4, ("Newly Released Movies", "%s/index.php?sort=release&page=" % pw_url))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		if auswahl == "--- Search ---":
			self.suchen()
		else:
			self.session.open(PrimeWireFilmlisteScreen, url, auswahl)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			self.suchString = urllib.quote(callback).replace(' ', '+')
			auswahl = "--- Search ---"
			url = "%s/?keywords=%s&page=" % (pw_url, self.suchString)
			self.session.open(PrimeWireFilmlisteScreen, url, auswahl)

class PrimeWireFilmlisteScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Url, Genre):
		self.Url = Url
		self.Genre = Genre
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"yellow" : self.keyFilter,
			"green" : self.keyPageNumber,
			"blue" : self.keySort
		}, -1)

		self['title'] = Label("PrimeWire")
		self['ContentTitle'] = Label("Genre: %s" % self.Genre)
		self['Page'] = Label(_("Page:"))
		self['F2'] = Label(_("Page"))
		self['F3'] = Label(_("Filter"))
		if not re.match(".*?Popular TV Shows|--- Search ---", self.Genre):
			self['F4'] = Label(_("Sort"))

		self.streamList = []
		self.handlung = ""
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.sort = None
		self.filter = None
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		url = "%s%s" % (self.Url, str(self.page))
		if self.sort:
			url = "%s&sort=%s" % (url, self.sort)
		if self.filter:
			url = "%s&country=%s" % (url, self.filter)
		twAgentGetPage(url, agent=pw_agent, cookieJar=pw_cookies).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.lastpage = re.findall('<div class="number_movies_result">(.*?)\sitems found</div>', data)
		if self.lastpage:
			self.lastpage = int(self.lastpage[0].replace(',',''))/24+1
		else:
			self.lastpage = 999
		self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		chMovies = re.findall('<div\sclass="index_item\sindex_item_ie">.*?<a\shref="(.*?)"\stitle="(.*?)"><img\ssrc="(.*?)"', data, re.S)
		if chMovies:
			for (chUrl,chTitle,chImage) in chMovies:
				chUrl = pw_url + "/" + chUrl
				chImage = pw_url + chImage
				self.streamList.append((decodeHtml(chTitle),chUrl,chImage))
		if len(self.streamList) == 0:
			self.streamList.append((_('No videos found!'), '', None))
		self.ml.setList(map(self._defaultlistleft, self.streamList))
		self.keyLocked = False
		self.th_ThumbsQuery(self.streamList,0,1,2,None,None, self.page, self.lastpage)
		self.showInfos()

	def showInfos(self):
		self.image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(self.image, agent=pw_agent, cookieJar=pw_cookies)
		url = self['liste'].getCurrent()[0][1]
		twAgentGetPage(url, agent=pw_agent, cookieJar=pw_cookies).addCallback(self.showInfos2).addErrback(self.dataError)

	def showInfos2(self, data):
		Handlung = re.search('display:block;">(.*?)</p></td>', data, re.S)
		if Handlung:
			self.handlung = Handlung.group(1).strip()
		else:
			self.handlung = ""
		self['handlung'].setText(decodeHtml(self.handlung))

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Link = self['liste'].getCurrent()[0][1]
		Name = self['liste'].getCurrent()[0][0]
		self.session.open(PrimeWireStreamsScreen, Link, Name, self.image, self.handlung)

	def keySort(self):
		if self.keyLocked or re.match(".*?Popular TV Shows|--- Search ---", self.Genre):
			return
		rangelist = [ ['Alphabet', 'alphabet'], ['Data Added', 'date'], ['Popular', 'views'], ['Ratings','ratings'], ['Favorites','favorites'], ['Release Date', 'release'],['Featured','featured']]
		self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keySortAction(self, result):
		if result:
			self['F4'].setText(result[0])
			self.sort = result[1]
			self.page = 1
			self.loadPage()

	def keyFilter(self):
		if self.keyLocked:
			return
		rangelist = [ ['All', ''], ['Germany', 'Germany'], ['USA', 'USA'], ['UK', 'UK'], ['Netherlands','Netherlands'], ['Austria','Austria'], ['Greece','Greece'], ['Russia','Russia'], ['Spain', 'Spain'], ['Turkey','Turkey']]
		self.session.openWithCallback(self.keyFilterAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keyFilterAction(self, result):
		if result:
			self['F3'].setText(result[0])
			self.filter = result[1]
			self.page = 1
			self.loadPage()

class PrimeWireStreamsScreen(MPScreen):

	def __init__(self, session, Link, Name, Image, Handlung):
		self.Link = Link
		self.Name = Name
		self.image = Image
		self.handlung = Handlung
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel,
		}, -1)

		self['title'] = Label("PrimeWire")
		self['ContentTitle'] = Label("Streams: %s" % self.Name)

		self.tw_agent_hlp = TwAgentHelper()
		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		twAgentGetPage(self.Link, agent=pw_agent, cookieJar=pw_cookies).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		streams = re.findall('<a href="(/stream/.*?\.html)".*?version_host">(.*?)</', data, re.S)
		if streams:
			for (Url, StreamHoster) in streams:
				StreamHoster = StreamHoster.replace('vShare','vshare.eu')
				check = isSupportedHoster(StreamHoster)
				if check:
					Url = pw_url + Url
					self.streamList.append((check, Url))
			if len(self.streamList) == 0:
				self.streamList.append((_('No supported streams found!'), None))
			else:
				self.keyLocked = False
		else:
			self.streamList.append((_('No supported streams found!'), None))
		self.ml.setList(map(self._defaultlisthoster, self.streamList))
		self['handlung'].setText(self.handlung)
		CoverHelper(self['coverArt']).getCover(self.image, agent=pw_agent, cookieJar=pw_cookies)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		url = self['liste'].getCurrent()[0][1]
		twAgentGetPage(url, agent=pw_agent, cookieJar=pw_cookies).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		streams = re.findall('data-href="(.*?)"', data, re.S)
		if streams:
			get_stream_link(self.session).check_link(streams[0], self.got_link)

	def got_link(self, stream_url):
		self.session.open(SimplePlayer, [(self.Name, stream_url, self.image)], showPlaylist=False, ltype='primewire', cover=True)