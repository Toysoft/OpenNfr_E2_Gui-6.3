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
		self['name'] = Label(_("Please wait..."))

		self.keyLocked = True
		self.suchString = ''
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = baseurl + "/sendungen-a-z"
		twAgentGetPage(url, agent=agent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.filmliste.append(("Suche", '', default_cover))
		raw = re.findall('<li class="item.*?<a class="link" href="(.*?)" title="Sendungen mit (?:\w|0-9)">(.*?)</a>', data, re.S)
		if raw:
			for (Url, Title) in raw:
				Url = baseurl + Url
				self.filmliste.append((decodeHtml(Title), Url, default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "Suche":
			self.suchen(suggest_func=self.getSuggestions)
		else:
			self.session.open(dreisatSubScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "Suche"
			self.suchString = callback
			Link = urllib.quote(self.suchString).replace(' ', '+')
			self.session.open(dreisatListScreen, Link, Name)

	def getSuggestions(self, text, max_res):
		url = "%s/search/typeahead?context=user&q=%s" % (apiurl, urllib.quote_plus(text))
		d = twAgentGetPage(url, agent=agent, headers={'Api-Auth':'Bearer 22918a9c7a733c027addbcc7d065d4349d375825'}, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, err=True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and type(suggestions) in (str, buffer):
			suggestions = json.loads(suggestions)
			for item in suggestions['http://zdf.de/rels/search/typeahead-suggestions']:
				li = item['text']
				list.append(str(li))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

class dreisatSubScreen(MPScreen):

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
		raw = re.findall('data-module="teaser-small".*?data-src="(.*?)".*?href="(.*?)".*?clickarea-link">(.*?)</p>', data, re.S)
		if raw:
			for (Image, Url, Title) in raw:
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_("No contents / results found!"), None, default_cover))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		coverUrl = self['liste'].getCurrent()[0][2]
		self['name'].setText(title)
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
		raw = re.findall('class="m--content-module.*?teaser-image="\[(.*?),.*?toggle-title="(.*?)".*?<span class="label">(.*?)</span>.*?href="(.*?)".*?paragraph-large\s{0,2}">(.*?)</p>', data, re.S)
		if raw:
			for (Image, Title, Runtime, Url, Handlung) in raw:
				Handlung = "Laufzeit: " + Runtime + "\n\n" + decodeHtml(Handlung).strip()
				self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
		raw = re.findall('class="video-carousel-item">.*?"title":\s"(.*?)",.*?duration":\s"(.*?)",.*?"embed_content":\s"(.*?)",.*?teaser-image-overwrite=[\"|\']\{"\d+x\d+":"(.*?)",', decodeHtml(data), re.S)
		if raw:
			for (Title, Runtime, Url, Image) in raw:
				Url = Url + ".html"
				Runtime = "Laufzeit: " + Runtime
				self.filmliste.append((decodeHtml(Title).strip().replace('\\"','"'), Url, Image.replace('\/','/'), Runtime))
		raw = re.findall('data-module="teaser-small".*?data-src="(.*?)".*?href="(.*?)".*?clickarea-link">(.*?)</p>.*?class="label">(.*?)</span>.*?clickarea-link"\s{0,1}>(.*?)</p>', data, re.S)
		if raw:
			for (Image, Url, Title, Runtime, Handlung) in raw:
				Handlung = "Laufzeit: " + Runtime + "\n\n" + decodeHtml(Handlung).strip()
				self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
		raw = re.findall('sophoraId":\s"(.*?)",.*?teaserHeadline":\s"(.*?)",.*?teasertext":\s"(.*?)",', decodeHtml(data), re.S)
		if raw:
			topurl = re.search('class="cluster-skip js-rb-click js-track-click" href="(.*?)#skip', decodeHtml(data), re.S)
			if topurl:
				for (Id, Title, Handlung) in raw:
					Url = topurl.group(1) + "/" + Id + ".html"
					Image = None
					self.filmliste.append((decodeHtml(Title).strip().replace('\\"','"'), Url, Image, decodeHtml(Handlung).strip().replace('\\"','"'), Id))
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
		if handlung:
			self['handlung'].setText(decodeHtml(handlung))
		else:
			self['handlung'].setText('')
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		self['name'].setText(_("Please wait..."))
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
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