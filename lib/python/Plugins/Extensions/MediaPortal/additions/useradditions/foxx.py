# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

BASE_URL = "http://foxx.to/"
fx_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
fx_cookies = {}

class foxxGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("foxx.to")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.genreData)

	def genreData(self):
		self.genreliste.append(("Neueste", "film"))
		self.genreliste.append(("Action", "genre/action"))
		self.genreliste.append(("Animation", "genre/animation"))
		self.genreliste.append(("Comedy", "genre/comedy"))
		self.genreliste.append(("Drama", "genre/drama"))
		self.genreliste.append(("Fantasy", "genre/fantasy"))
		self.genreliste.append(("Horror", "genre/horror"))
		self.genreliste.append(("Mystery", "genre/mystery"))
		self.genreliste.append(("Romance", "genre/romance"))
		self.genreliste.append(("Sci-Fi", "genre/science-fiction"))
		self.genreliste.append(("Thriller", "genre/thriller"))
		self.genreliste.append(("Western", "genre/western"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(foxxFilmScreen, Link, Name)

class foxxFilmScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("foxx.to")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.filmliste = []
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		url = BASE_URL + self.Link + "/page/" + str(self.page)
		getPage(url, agent=fx_agent, cookies=fx_cookies).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.getLastPage(data, '', ">Seite.*?von\s(\d+)</span")
		filme = re.findall('class="poster">.{0,1}<img\ssrc="(.*?)"\salt="(.*?)".*?<a\shref="(http://foxx.to/film/.*?-Stream)">', data, re.S)
		if filme:
			for (image, title, url) in filme:
				self.filmliste.append((decodeHtml(title), url, image))
			if len(self.filmliste) == 0:
				self.filmliste.append((_('No videos found!'), '', None))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.ml.moveToIndex(0)
			self.keyLocked = False
			self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][2]
		self['name'].setText(Title)
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		getPage(url, agent=fx_agent, cookies=fx_cookies).addCallback(self.gotPage).addErrback(self.dataError)

	def gotPage(self, data):
		view = re.findall('(http://foxx.to/view.php\?url=.*?)"', data, re.S)
		if view:
			url = view[0]
			getPage(url, agent=fx_agent, cookies=fx_cookies).addCallback(self.gotStream).addErrback(self.dataError)

	def gotStream(self, data):
		try:
			import execjs
			node = execjs.get("Node")
		except:
			printl('nodejs not found',self,'E')
			self.session.open(MessageBoxExt, _("This plugin requires packages python-pyexecjs and nodejs."), MessageBoxExt.TYPE_INFO)
			return
		decoder = "decrypt=function(s) {"\
			"var e={},i,b=0,c,x,l=0,a,r='',w=String.fromCharCode,L=s.length;"\
			"var A='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';"\
			"for(i=0;i<64;i++){e[A.charAt(i)]=i;}"\
			"for(x=0;x<L;x++){"\
			"	c=e[s.charAt(x)];b=(b<<6)+c;l+=6;"\
			"	while(l>=8){((a=(b>>>(l-=8))&0xff)||(x<(L-2)))&&(r+=w(a));}}"\
			"return r;};"
		video_url = re.findall('var jbdaskgs\s=.\'(.*?)\'\s;', data, re.S)
		js = decoder + "\n" + 'video_url=decrypt(\''+video_url[0]+'\');' + "return video_url;"
		urls = str(node.exec_(js))
		streams = re.findall('"file":"(.*?)","label":"(\d+)', urls, re.S)
		stream_url = None
		if streams:
			res = 0
			for stream in streams:
				if int(stream[1]) > res:
					res = int(stream[1])
					stream_url = str(stream[0])
		else:
			streams = re.findall('"file":"(.*?)"', urls, re.S)
			if streams:
				stream_url = streams[0]
		if stream_url:
			Title = self['liste'].getCurrent()[0][0]
			Image = self['liste'].getCurrent()[0][2]
			self.session.open(SimplePlayer, [(Title, stream_url, Image)], cover=True, showPlaylist=False, ltype='foxx.to')