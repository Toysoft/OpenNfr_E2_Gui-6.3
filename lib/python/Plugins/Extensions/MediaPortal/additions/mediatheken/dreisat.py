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
import requests

baseurl = "https://www.3sat.de"
apiurl = "https://api.3sat.de"
default_cover = "file://%s/3sat.png" % (config_mp.mediaportal.iconcachepath.value + "logos")
agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36"

class dreisatGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("3sat Mediathek")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.suchString = ''
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.parseData)

	def parseData(self):
		self.filmliste.append(("Suche", '', default_cover))
		self.filmliste.append(("Sendung verpasst!?", '', default_cover))
		self.filmliste.append(("Sendungen A-Z", '/sendungen-a-z', default_cover))
		self.filmliste.append(("Themen", '/themen', default_cover))
		self.filmliste.append(("Kultur", '/kultur', default_cover))
		self.filmliste.append(("Wissen", '/wissen', default_cover))
		self.filmliste.append(("Gesellschaft", '/gesellschaft', default_cover))
		self.filmliste.append(("Film", '/film', default_cover))
		self.filmliste.append(("Dokumentation", '/dokumentation', default_cover))
		self.filmliste.append(("Kabarett", '/kabarett', default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "Suche":
			self.suchen()
		elif Name == 'Sendung verpasst!?':
			self.session.open(dreisatDateScreen, Link, Name)
		elif Name == "Sendungen A-Z":
			self.session.open(dreisatGenreSubScreen, Link, Name)
		elif Name == "Themen":
			self.session.open(dreisatGenreSubScreen, Link, Name)
		else:
			Link = baseurl + Link
			self.session.open(dreisatListScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "Suche"
			self.suchString = callback
			Link = urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(dreisatListScreen, Link, Name)

class dreisatGenreSubScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("3sat Mediathek")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['name'] = Label(_("Please wait..."))

		self.keyLocked = True
		self.suchString = ''
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = baseurl + self.Link
		twAgentGetPage(url, agent=agent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		if self.Name == "Sendungen A-Z":
			raw = re.findall('<li class="item.*?<a class="link" href="(.*?)" title="Sendungen mit (?:\w|0-9)">(.*?)</a>', data, re.S)
			if raw:
				for (Url, Title) in raw:
					Url = baseurl + Url
					self.filmliste.append((decodeHtml(Title), Url, default_cover, None))
		else:
			raw = re.findall('class="m--content-module.*?data-src="(.*?)".*?href="(.*?)".*?headline level-4\s+">(.*?)</h3>.*?paragraph-large\s{0,2}">(.*?)</p>', data, re.S)
			if raw:
				for (Image, Url, Title, Handlung) in raw:
					Url = baseurl + Url
					self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
			raw = re.findall('class="m--teaser-topic.*?data-src="(.*?)".*?href="(.*?)".*?class="a--headline.*?>(.*?)</h3>.*?class="a--subheadline.*?>(.*?)</p>', data, re.S)
			if raw:
				for (Image, Url, Title, Handlung) in raw:
					Url = baseurl + Url
					self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
			raw = re.findall('class="m--teaser-small.*?data-src="(.*?)".*?href="(.*?)".*?class="a--headline.*?clickarea-link">(.*?)</p>.*?class="a--subheadline.*?>(.*?)</p>', data, re.S)
			if raw:
				for (Image, Url, Title, Handlung) in raw:
					Url = baseurl + Url
					self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		coverUrl = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][3]
		self['name'].setText(title)
		if handlung:
			self['handlung'].setText(decodeHtml(handlung))
		else:
			self['handlung'].setText('')
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if self.Name == "Sendungen A-Z":
			self.session.open(dreisatAZScreen, Link, Name)
		else:
			self.session.open(dreisatListScreen, Link, Name)

class dreisatDateScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("3sat Mediathek")
		self['ContentTitle'] = Label("Sendung verpasst!?")
		self['name'] = Label(_("Selection:"))

		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		today = datetime.date.today()
		for daynr in range(-21,15):
			day1 = today - datetime.timedelta(days=daynr)
			dateselect = day1.strftime('%Y-%m-%d')
			link = '%s/programm?airtimeDate=%s' % (baseurl, dateselect)
			self.filmliste.append((dateselect, link, ''))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.ml.moveToIndex(21)
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(dreisatListScreen, Link, Name)

class dreisatAZScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("3sat Mediathek")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['name'] = Label(_("Please wait..."))

		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		twAgentGetPage(self.Link, agent=agent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('data-module="teaser-small".*?data-src="(.*?)".*?href="(.*?)".*?clickarea-link">(.*?)</p>.*?class="a--subheadline.*?>(.*?)</p>', data, re.S)
		if raw:
			for (Image, Url, Title, Handlung) in raw:
				self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
		if len(self.filmliste) == 0:
			self.filmliste.append((_("No contents / results found!"), None, default_cover))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		coverUrl = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][3]
		self['name'].setText(title)
		if handlung:
			self['handlung'].setText(decodeHtml(handlung))
		else:
			self['handlung'].setText('')
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Link:
			Link = baseurl + Link
			self.session.open(dreisatListScreen, Link, Name)

class dreisatListScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_Plugin', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"	: self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("3sat Mediathek")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['name'] = Label(_("Please wait..."))

		self.keyLocked = True
		self.filmliste = []
		self.page = 1
		self.lastpage = 1
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		if re.match(".*Suche", self.Name):
			self.filmliste = []
			self.lastpage = 999
			self['Page'].setText(_("Page:"))
			self['page'].setText(str(self.page))
			url = baseurl + "/suche?q=%s&synth=true&attrs=&contentTypes=episode&page=%s" % (self.Link, str(self.page))
		else:
			url = self.Link
		twAgentGetPage(url, agent=agent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		if re.match('\d{4}-\d{2}-\d{2}', self.Name):
			raw = re.findall('class="m--teaser-epg js-teaser-article is-video.*?data-src="(.*?)".*?airtime-begin class="time">(.*?)</span>.*?class="a--headline.*?>(.*?)</h3>.*?class="label">(.*?)</span>.*?data-teasertext.*?>(.*?)(?:</p>|<br />).*?href="(.*?)"', data, re.S)
			if raw:
				for (Image, Airtime, Title, Runtime, Handlung, Url) in raw:
					Title = Airtime + " - " + decodeHtml(Title)
					Handlung = "Laufzeit: " + Runtime + "\n\n" + decodeHtml(Handlung).replace('<b>','').replace('</b>','').strip()
					self.filmliste.append((Title, Url, Image, Handlung))
		else:
			raw = re.findall('class="m--content-module.*?title":\s"(.*?)",.*?"duration":\s"(.*?)".*?"embed_content":\s"(.*?)",.*?teaser-image="\[(.*?),(.*?)class="teaser-info', decodeHtml(data), re.S)
			if raw:
				for (Title, Runtime, Embed, Image, Meta) in raw:
					url = re.findall('href="(.*?)"', Meta, re.S)
					if url:
						Url = url[0]
					else:
						Url = Embed + ".html"
					handlung = re.findall('paragraph-large\s{0,2}">(.*?)</p>', Meta, re.S)
					Handlung = "Laufzeit: " + Runtime + "\n\n" + decodeHtml(handlung[0]).strip()
					self.filmliste.append((decodeHtml(Title).replace('\/','/'), Url, Image, Handlung))
			raw = re.findall('class="video-carousel-item">.*?"title":\s"(.*?)",.*?duration":\s"(.*?)",.*?"embed_content":\s"(.*?)",.*?teaser-image-overwrite=[\"|\']\{"\d+x\d+":"(.*?)",', decodeHtml(data), re.S)
			if raw:
				for (Title, Runtime, Url, Image) in raw:
					Url = Url + ".html"
					Runtime = "Laufzeit: " + Runtime
					self.filmliste.append((decodeHtml(Title).strip().replace('\\"','"').replace('\/','/'), Url, Image.replace('\/','/'), Runtime))
			raw = re.findall('<article class="m--teaser-small.*?data-src="(.*?)".*?href="(.*?)".*?<h3(.*?)</article>', data, re.S)
			if raw:
				for (Image, Url, Meta) in raw:
					meta = re.findall('clickarea-link">(.*?)</p>.*?class="label">(.*?)</span>.*?clickarea-link"\s{0,1}>(.*?)</p>', Meta, re.S)
					if meta:
						Handlung = "Laufzeit: " + meta[0][1] + "\n\n" + decodeHtml(meta[0][2]).strip()
						self.filmliste.append((decodeHtml(meta[0][0]), Url, Image, Handlung))
			raw = re.findall('sophoraId":\s"(.*?)",.*?teaserHeadline":\s"(.*?)",.*?teasertext":\s"(.*?)",', decodeHtml(data), re.S)
			if raw:
				topurl = re.search('class="cluster-skip js-rb-click js-track-click" href="(.*?)#skip', decodeHtml(data), re.S)
				if topurl:
					for (Id, Title, Handlung) in raw:
						Url = topurl.group(1) + "/" + Id + ".html"
						Image = None
						self.filmliste.append((decodeHtml(Title).strip().replace('\\"','"').replace('\/','/'), Url, Image, decodeHtml(Handlung).strip().replace('\\"','"'), Id))
		if len(self.filmliste) == 0:
			self.filmliste.append((_("No videos found!"), None, default_cover, ""))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		coverUrl = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][3]
		self['name'].setText(title)
		if not coverUrl:
			Id = self['liste'].getCurrent()[0][4]
			teaserurl = baseurl + "/teaserElement?sophoraId=%s&style=m2&moduleId=mod-2&teaserHeadline=&clusterTitle=Alle+Sendungen&clusterType=Cluster_S&sourceModuleType=cluster-s" % str(Id)
			try:
				s = requests.session()
				page = s.get(teaserurl, timeout=5)
				teaserdata = page.content
				teaser = re.findall('data-module="teaser-small".*?data-src="(.*?)".*?<div class="ratio-inner">(.*?)class="info-panel-content".*?clickarea-link"\s{0,1}>(.*?)</p>', teaserdata, re.S)
				if teaser:
					for (Image, RuntimeData, Handlung) in teaser:
						if RuntimeData:
							Runtime = re.search('class="label">(.*?)</span>', RuntimeData, re.S)
							if Runtime:
								handlung = "Laufzeit: " + Runtime.group(1) + "\n\n" + decodeHtml(Handlung).strip()
							else:
								handlung = decodeHtml(Handlung).strip()
						else:
							handlung = decodeHtml(Handlung).strip()
						coverUrl = Image
			except:
				pass
		if handlung:
			self['handlung'].setText(decodeHtml(handlung))
		else:
			self['handlung'].setText('')
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink:
			self['name'].setText(_("Please wait..."))
			Link = baseurl + streamLink
			twAgentGetPage(Link, agent=agent).addCallback(self.getToken).addErrback(self.dataError)

	def getToken(self,data):
		token = re.findall('data-zdfplayer-jsb.*?apiToken":\s"(.*?)",', data, re.S)
		if token:
			self.token = token[0]
			streamLink = self['liste'].getCurrent()[0][1]
			Link = apiurl + "/content/documents/zdf" +  streamLink.replace('.html','.json') + "?profile=player2"
			twAgentGetPage(Link, agent=agent, headers={'Api-Auth':'Bearer %s' % self.token, 'Accept':'application/vnd.de.zdf.v1.0+json'}).addCallback(self.getTemplateJson).addErrback(self.dataError)
		else:
			self.keyLocked = False
			streamName = self['liste'].getCurrent()[0][0]
			self['name'].setText(streamName)

	def getTemplateJson(self,data):
		a = json.loads(data)
		try:
			url = apiurl + str(a['location'])
			twAgentGetPage(url, agent=agent, headers={'Api-Auth':'Bearer %s' % self.token, 'Accept':'application/vnd.de.zdf.v1.0+json'}).addCallback(self.getTemplateJson).addErrback(self.dataError)
		except:
			b = a['mainVideoContent']['http://zdf.de/rels/target']['http://zdf.de/rels/streams/ptmd-template']
			if b:
				b = b.replace('{playerId}','ngplayer_2_3')
				b = apiurl +b
				twAgentGetPage(str(b), agent=agent, headers={'Api-Auth':'Bearer %s' % self.token, 'Accept':'application/vnd.de.zdf.v1.0+json'}).addCallback(self.getContentJson).addErrback(self.dataError)

	def getContentJson(self,data):
		a = json.loads(data)
		b = []
		for x in range (0,5,1):
			try:
				b.append((a['priorityList'][1]['formitaeten'][0]['qualities'][x]['audio']['tracks'][0]['uri']))
			except:
				break
		self.keyLocked = False
		streamName = self['liste'].getCurrent()[0][0]
		c = b[0]
		c = c.replace("1496k","3296k")
		c = c.replace("p13v13","p15v13")
		c = c.replace("p13v14","p15v14")
		url = str(c).replace("https","http")
		if '.f4m' in url:
			b = []
			for x in range (0,5,1):
				try:
					b.append((a['priorityList'][0]['formitaeten'][0]['qualities'][x]['audio']['tracks'][0]['uri']))
				except:
					break
			self.keyLocked = False
			url = str(b[0])
		playlist = []
		playlist.append((streamName, url))
		self.session.open(SimplePlayer, playlist, showPlaylist=False, ltype='3sat')
		self['name'].setText(streamName)