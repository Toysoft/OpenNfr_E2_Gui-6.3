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
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper
import requests
agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
default_cover = "file://%s/freeones.png" % (config_mp.mediaportal.iconcachepath.value + "logos")

class freeonesGenreScreen(MPScreen):

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

		self['title'] = Label("FreeOnes.com")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "https://videos.freeones.com/categories/"
		twAgentGetPage(url, agent=agent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('class="catBlock".*?href="(.*?)".*?>(.*?)<img\ssrc="(.*?)"', data, re.S)
		if Cats:
			for (Url, Title, Image) in Cats:
				Url = "https://videos.freeones.com" + Url
				Title = Title.strip()
				self.genreliste.append((Title, Url, Image))
		self.genreliste.sort()
		self.genreliste.insert(0, ("Longest", "https://videos.freeones.com/all-videos/duration/", default_cover))
		self.genreliste.insert(0, ("Full-Videos - Most Viewed", "https://videos.freeones.com/full-videos/views/", default_cover))
		self.genreliste.insert(0, ("Full-Videos - Most Popular", "https://videos.freeones.com/full-videos/rank/", default_cover))
		self.genreliste.insert(0, ("Full-Videos - Latest", "https://videos.freeones.com/full-videos/date/", default_cover))
		self.genreliste.insert(0, ("Most Viewed", "https://videos.freeones.com/all-videos/views/", default_cover))
		self.genreliste.insert(0, ("Most Popular", "https://videos.freeones.com/all-videos/rank/", default_cover))
		self.genreliste.insert(0, ("Latest", "https://videos.freeones.com/all-videos/date/", default_cover))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", default_cover))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image, agent=agent)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen(suggest_func=self.getSuggestions)
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(freeonesFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = urllib.quote(callback).replace(' ', '+')
			self.session.open(freeonesFilmScreen, Link, Name)

	def getSuggestions(self, text, max_res):
		url = "https://www.freeones.com/suggestions.php?q=%s&t=8" % urllib.quote_plus(text)
		d = twAgentGetPage(url, agent=agent, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, err=True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and type(suggestions) in (str, buffer):
			suggestions = re.findall('id="suggestion">(.*?)</div', suggestions, re.S)
			for item in suggestions:
				li = stripAllTags(item).strip('\'').strip()
				list.append(str(li))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

class freeonesFilmScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label("FreeOnes.com")
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
			url = "https://www.freeones.com/search/?t=8&q=%s&sq=&page=%s" % (self.Link, str(self.page))
		else:
			url = "%s%s.html" % (self.Link, str(self.page))
		twAgentGetPage(url, agent=agent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="Paging">(.*?)</div>', '.*[\/|>|\/](?:\s+|)(\d+)(?:\s+|)[\"|<|\.html]')
		Movies = re.findall('class="video_thumb.*?href="(.*?)">.*?<img.*?src="(.*?)".*?Views\s(\d+)\sDuration\s(.*?)(?:\s|</span).*?class="(?:video-info\s|)video-title">(.*?)</span', data, re.S)
		if Movies:
			for (Url, Image, Views, Runtime, Title) in Movies:
				Image = Image.replace('/small/','/poster/')
				self.filmliste.append((decodeHtml(Title), Url, Image, Runtime, Views))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		Url = self['liste'].getCurrent()[0][1]
		if Url == None:
			return
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		runtime = self['liste'].getCurrent()[0][3]
		views = self['liste'].getCurrent()[0][4]
		self['name'].setText(title)
		self['handlung'].setText("Runtime: %s\nViews: %s" % (runtime, views))
		CoverHelper(self['coverArt']).getCover(pic, agent=agent)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link == None:
			return
		self.keyLocked = True
		twAgentGetPage(Link, agent=agent).addCallback(self.getVideoPage).addErrback(self.dataError)

	def getVideoPage(self, data):
		videoPage = re.findall("streamingUrl:\s'(.*?)',", data, re.S)
		qualities = re.findall("qualities:\s'(.*?)'", data, re.S)
		if videoPage and qualities:
			self.keyLocked = False
			Title = self['liste'].getCurrent()[0][0]
			url = videoPage[0] + "/" + qualities[0].split(',')[0] + ".mp4"
			mp_globals.player_agent = agent
			self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='freeones')